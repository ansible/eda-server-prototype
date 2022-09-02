import logging
import os
from types import Iterable
from typing import Union
from uuid import uuid4
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ansible_events_ui.db.dependency import get_db_session


LOG = logging.getLogger("ansible_events_ui.lostream")
LOLOGLEVEL = "LOSTREAM_LOG_LEVEL"
if LOLOGLEVEL in os.environ:
    LOG.setLevel(
        getattr(
            logging,
            upper(os.environ.get(LOLOGLEVEL, "INFO")),
        )
    )


# Default read buffer size is
CHUNK_SIZE = 1024 ** 2


# Class that will use server-side functions to access
# PostgreSQL large object
class LObject(Iterable):
    """
    Facilitate PostgreSQL large object functionality using the
    PostgreSQL server-side functions.

    As of 2022-09-01, there is no large object support directly
    in asyncpg or other async Python PostgreSQL drivers.
    """
    VALID_MODES = {"rwt", "rt", "wt", "at", "rwb", "rb", "wb", "ab"}
    INV_READ = 0x00040000
    INV_WRITE = 0x00020000
    MODE_MAP = {
        "r": INV_READ,
        "W": INV_WRITE,
        'a' : INV_READ | INV_WRITE
    }

    async def __init__(
        self: "LObject",
        oid: int = 0,
        session: AsyncSession = Depends(get_db_session()),
        *,
        chunk_size: int = CHUNK_SIZE,
        mode: str = "rb",
    ):
        self.session = session
        self.chunk_size = chunk_size if chunk_size > 0 else CHUNK_SIZE
        self.oid = oid

        self._exists, self.length = await self.exists()

        self.imode, self.text_data, self.append = self._resolve_mode(mode)
        self.pos = self.length if self.append else 0

        if not self._exists:
            await self.create()
            self.created = True
        else:
            self.created = False

    def _resolve_mode(self: "LObject", mode: str):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Mode {mode} must be one of {sorted(self.VALID_MODES)}")

        _text_data = self.mode.endswith("t")
        _append = self.mode.startswith("a")
        _mode = 0
        for c in mode:
            if c in "arw":
                _mode | self.MODE_MAP[c]

        return _mode, _text_data, _append

    async def __aenter__(self) -> "LObject":
        return self

    async def __aexit__(self: "LObject", *aexit_stuff: Tuple) -> None:
        await self.exit_handler()

    async def __del__(self: "LObject") -> None:
        await self.exit_handler()

    async def __aiter__(self: "LObject") -> Iterable:
        self.pos = 0
        return self

    async def __anext__(self) -> Union[str, bytes]:
        if self.pos < self.length:
            buff = await self.read()
            return buff
        else:
            raise StopAsyncIteration()

    async def read(self: "LObject") -> Union[bytes, str]:
        sql = """
select lo_get(%s, %s, %s) as lo_bytes
;
"""
        buff = b'\x00'
        cur = await self.session.execute(sql, (self.oid, self.pos, self.chunk_size))
        res = cur.first()
        buff = getattr(res, 'lo_bytes', b'')
        self.pos += len(buff)

        return buff.decode("utf-8") if self.text_data else buff

    async def write(self: "LObject", buff: Union[str, bytes]) -> int:
        if len(buff) > 0:
            sql = """
select lo_put(%s, %s, %s) as lo_bytes
;
"""
            if self.text_data and isinstance(buff, str):
                buff = buff.encode("utf-8")

            bufflen = len(buff)
            await self.session.execute(sql, (self.oid, self.pos, buff))
            self.pos += bufflen

            return bufflen
        else:
            return 0

    async def create(self) -> None:
        cur = await self.session.execute(
            """
select lo_create(0) as loid
;
            """
        )
        res = cur.first()
        if res and res.loid > 0:
            self.oid = res.loid

    async def exists(self) -> tuple:
        cur = await self.session.execute(
            """
select m.oid,
       sum(length(coalesce(d.data, convert_to('', 'utf-8')))) as _length
  from pg_largeobject_metadata m
  left
  join pg_largeobject d
    on d.loid = m.oid
 where m.oid = %s
 group
    by m.oid
;
            """,
            (self.oid,)
        )
        res = await cur.first()
        if res is None:
            return False, 0
        else:
            return res.oid, res._length

    async def open(self: "LObject", _oid: int = 0, _mode: str = "") -> None:
        if _mode:
            imode, *_ = self._resolve_mode(_mode)
        else:
            imode = self.imode

        if _oid <= 0:
            _oid = self.oid

        if _mode and self._fd is None and _oid > 0:
            cur = self.session.execute(
                """
select lo_open(%s, %s) as loid
;
                """,
                _oid,
            )
            res = cur.first()
            if res:
                self._fd = res.loid

    async def close(self: "LObject") -> None:
        if self._fd is not None:
            await self.session.execute(
                """
select lo_close(%s) ;
                """,
                (self._fd,)
            )
            self._fd = None

    async def exit_handler(self: "LObject"):
        # Truncate on (over)write.
        if self.oid and not self.append and self.imode & self.INV_WRITE:
            await self.open(_oid=self.oid, _mode="rw")
            await self.truncate(self.pos)
            await self.close()
            self.imode = 0
