from __future__ import annotations

import logging
from io import UnsupportedOperation
from typing import List, Tuple, Union

from sqlalchemy import column, func, select, text
from sqlalchemy.dialects.postgresql import ARRAY, OID, array
from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_dbapi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce, sum as sum_

LOG = logging.getLogger(__name__)
VALID_MODES = {"rwt", "rt", "wt", "at", "rwb", "rb", "wb", "ab"}
INV_READ = 0x00040000
INV_WRITE = 0x00020000
MODE_MAP = {"r": INV_READ, "w": INV_WRITE, "a": INV_READ | INV_WRITE}

DEFAULT_BYTE_ENCODING = "utf-8"

# Default chunked buffer size intended for read
CHUNK_SIZE = 1024**2


class PGLargeObjectNotFound(AsyncAdapt_asyncpg_dbapi.IntegrityError):
    pass


class PGLargeObjectUnsupportedOp(UnsupportedOperation):
    pass


class PGLargeObjectClosed(AsyncAdapt_asyncpg_dbapi.DatabaseError):
    pass


class PGLargeObject:
    """
    Facilitate PostgreSQL large object interface using server-side functions.

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
                                    "rwt", "rt", "wt", "at",
                                    "rwb", "rb", "wb", "ab"
                                    r = read (object must exist)
                                    w = write (object will be created)
                                    rw = read/write
                                    a = read/write, but initialize
                                        file pointer for append.
                                    mode must end with 'b' or 't'
                                    b = binary data in and out
                                    t = text data in and out
                                    Data are converted accordingly.
        encoding: str           =   encoding to use
                                    default is the same as
                                    str.encode() ('utf-8')
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
        self.encoding = encoding

        self.imode, self.text_data, self.append = self.resolve_mode(mode)
        self.pos = self.length if self.append else 0

    async def __aenter__(self) -> PGLargeObject:
        await self.open()
        return self

    async def __aexit__(self, *aexit_stuff: Tuple) -> None:
        await self.close()
        return None

    @staticmethod
    def resolve_mode(mode: str) -> Tuple:
        if mode not in VALID_MODES:
            raise ValueError(
                f"Mode {mode} must be one of {sorted(VALID_MODES)}"
            )

        text_data = mode.endswith("t")
        append = mode.startswith("a")
        imode = 0
        for c in mode:
            imode |= MODE_MAP.get(c, 0)

        return imode, text_data, append

    @staticmethod
    async def create_large_object(session: AsyncSession) -> int:
        sql = select(func.lo_create(0).label("loid"))
        oid = await session.scalar(sql)
        return oid

    @staticmethod
    async def verify_large_object(session: AsyncSession, oid: int) -> Tuple:
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
            rec = (None, None)
        return rec

    @staticmethod
    async def delete(session: AsyncSession, oids: List[int]) -> None:
        if oids and all(o > 0 for o in oids):
            sql = select(func.lo_unlink(text("oid"))).select_from(
                func.unnest(array(oids, type_=ARRAY(OID))).alias("oid")
            )
            await session.execute(sql)

    def closed_check(self):
        if self.closed:
            raise PGLargeObjectClosed("Large object is closed")

    async def gread(self) -> Union[bytes, str]:
        self.pos = 0
        while True:
            buff = await self.read()
            if not buff:
                break
            yield buff

    async def read(self) -> Union[bytes, str]:
        self.closed_check()
        if self.imode == INV_WRITE:
            raise PGLargeObjectUnsupportedOp("not readable")

        sql = select(func.lo_get(self.oid, self.pos, self.chunk_size))
        buff = await self.session.scalar(sql)
        if buff is None:
            buff = b""

        self.pos += len(buff)

        return buff.decode(self.encoding) if self.text_data else buff

    async def write(self, buff: Union[str, bytes]) -> int:
        self.closed_check()
        if self.imode == INV_READ:
            raise PGLargeObjectUnsupportedOp("not writeable")

        if not buff:
            return 0

        # Large objects store bytes only.
        if isinstance(buff, str):
            buff = buff.encode(self.encoding)

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
