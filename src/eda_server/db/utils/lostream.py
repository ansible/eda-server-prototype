#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import logging
from typing import AsyncIterator, List, Tuple, Union

from sqlalchemy import column, func, select, text
from sqlalchemy.dialects.postgresql import ARRAY, OID, array
from sqlalchemy.exc import DatabaseError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce, sum as sum_

LOG = logging.getLogger(__name__)
VALID_MODES = {"rw", "r", "w", "a"}
INV_READ = 0x00040000
INV_WRITE = 0x00020000
MODE_MAP = {"r": INV_READ, "w": INV_WRITE, "a": INV_READ | INV_WRITE}

DEFAULT_BYTE_ENCODING = "utf-8"

# Default chunked buffer size intended for read
CHUNK_SIZE = 1024**2


class PGLargeObjectError(Exception):
    pass


class PGLargeObjectNotCreated(PGLargeObjectError, DatabaseError):
    pass


class PGLargeObjectNotFound(PGLargeObjectError, NoResultFound):
    pass


class PGLargeObjectUnsupportedOp(PGLargeObjectError):
    pass


class PGLargeObjectClosed(PGLargeObjectUnsupportedOp):
    pass


class PGLargeObject:
    """
    Facilitate PostgreSQL large object interface using server-side functions.

    This class operates on buffers that are `bytes` type.

    As of 2022-09-01, there is no large object support directly
    in asyncpg or other async Python PostgreSQL drivers.

    Usage:
        With context:
            async with PGLargeObject(session, oid, ...) as PGLargeObject:
                # Read up to CHUNK_SIZE (defined in module)
                buff = async PGLargeObject.read()

        Direct:
            PGLargeObject = PGLargeObject(session, oid, mode="wt")
            PGLargeObject.open()
            PGLargeObject.write("Some data...")
            PGLargeObject.close()

    Parameters:
        session: AsyncSession
        oid: int                = oid of large object
        chunk_size: int         = read in chunks of chunk_size (set only
                                = once at instantiation.)
        mode: str               = How object is to be opened:
                                  Valid values:
                                    "rw", "r", "w", "a",
                                    r = read (object must exist)
                                    w = write (object will be created)
                                    rw = read/write
                                    a = read/write, but initialize
                                        file pointer for append.
    """

    def __init__(
        self,
        session: AsyncSession,
        oid: int = 0,
        mode: str = "rb",
        *,
        chunk_size: int = CHUNK_SIZE,
        encoding: str = DEFAULT_BYTE_ENCODING,
    ):
        self.session = session
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be an integer greater than zero."
            )
        self.chunk_size = chunk_size
        self.oid = oid
        self.closed = False

        self.imode, self.append = self.resolve_mode(mode)
        self.pos = self.length if self.append else 0

    async def __aenter__(self) -> PGLargeObject:
        await self.open()
        return self

    async def __aexit__(self, *aexit_stuff: Tuple) -> None:
        await self.close()

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self

    async def __anext__(self) -> bytes:
        buff = await self.read()
        if not buff:
            raise StopAsyncIteration()
        return buff

    @staticmethod
    def resolve_mode(mode: str) -> Tuple[int, bool]:
        if mode not in VALID_MODES:
            raise ValueError(
                f"Mode {mode} must be one of {sorted(VALID_MODES)}"
            )

        append = mode.startswith("a")
        imode = 0
        for c in mode:
            imode |= MODE_MAP.get(c, 0)

        return imode, append

    @staticmethod
    async def create_large_object(session: AsyncSession) -> int:
        sql = select(func.lo_create(0).label("loid"))
        oid = await session.scalar(sql)
        if oid == 0:
            raise PGLargeObjectNotCreated(
                "Requested large object was not created."
            )
        return oid

    @staticmethod
    async def verify_large_object(
        session: AsyncSession, oid: int
    ) -> Tuple[bool, int]:
        sel_cols = [
            column("oid"),
            sum_(
                func.length(
                    coalesce(text("data"), func.convert_to("", "utf-8"))
                )
            ).label("data_length"),
        ]
        sql = (
            select(sel_cols)
            .select_from(text("pg_largeobject_metadata"))
            .join(
                text("pg_largeobject"),
                column("loid") == column("oid"),
                isouter=True,
            )
            .where(column("oid") == oid)
            .group_by(column("oid"))
        )
        rec = (await session.execute(sql)).first()
        if not rec:
            rec = (False, 0)
        return rec

    @staticmethod
    async def delete_large_object(
        session: AsyncSession, oids: List[int]
    ) -> None:
        if oids and all(o > 0 for o in oids):
            sql = select(func.lo_unlink(text("oid"))).select_from(
                func.unnest(array(oids, type_=ARRAY(OID))).alias("oid")
            )
            await session.execute(sql)

    def closed_check(self):
        if self.closed:
            raise PGLargeObjectClosed("Large object is closed")

    async def read(self) -> Union[bytes, str]:
        self.closed_check()

        if self.imode == INV_WRITE:
            raise PGLargeObjectUnsupportedOp(
                "Large Object class instance is set for write only"
            )

        sql = select(func.lo_get(self.oid, self.pos, self.chunk_size))
        buff = await self.session.scalar(sql)
        if buff is None:
            buff = b""

        self.pos += len(buff)

        return buff

    async def write(self, buff: bytes) -> int:
        self.closed_check()

        if self.imode == INV_READ:
            raise PGLargeObjectUnsupportedOp(
                "Large Object class instance is set for read only"
            )

        if not buff:
            return 0

        bufflen = len(buff)
        sql = select(func.lo_put(self.oid, self.pos, buff))
        await self.session.execute(sql)
        self.pos += bufflen
        self.writes += 1

        return bufflen

    async def truncate(self) -> None:
        self.closed_check()

        if self.imode == INV_READ:
            raise PGLargeObjectUnsupportedOp("not writeable")

        open_sql = select(func.lo_open(self.oid, self.imode))
        fd = await self.session.scalar(open_sql)

        trunc_sql = select(func.lo_truncate(fd, self.pos))
        await self.session.execute(trunc_sql)

        close_sql = select(func.lo_close(fd))
        await self.session.execute(close_sql)

        self.length = self.pos

    async def open(self) -> None:
        self.closed_check()

        exists, length = await self.verify_large_object(self.session, self.oid)
        if exists:
            self.length = length
        else:
            if not self.imode & INV_WRITE:
                raise PGLargeObjectNotFound(
                    f"Large object with oid {self.oid} does not exist."
                )
            else:
                self.oid = await self.create_large_object(self.session)
                self.length = self.pos = 0

        self.writes = 0

    async def close(self) -> None:
        if not self.closed and self.oid > 0 and self.writes > 0:
            await self.truncate()
        self.closed = True


def decode_bytes_buff(buff: bytes) -> Tuple[str, str]:
    convlen = len(buff)
    while convlen >= 0:
        try:
            obuff = (buff[:convlen]).decode()
        except UnicodeDecodeError:
            convlen -= 1
        else:
            break

    return obuff, buff[convlen:]
