import logging
from io import UnsupportedOperation
from typing import Tuple, Union

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db.dependency import get_db_session

LOG = logging.getLogger(__name__)


# Default read buffer size is
CHUNK_SIZE = 1024**2


class LObject:
    """
    Facilitate PostgreSQL large object interface using server-side functions.

    As of 2022-09-01, there is no large object support directly
    in asyncpg or other async Python PostgreSQL drivers.
    """

    VALID_MODES = {"rwt", "rt", "wt", "at", "rwb", "rb", "wb", "ab"}
    INV_READ = 0x00040000
    INV_WRITE = 0x00020000
    MODE_MAP = {"r": INV_READ, "w": INV_WRITE, "a": INV_READ | INV_WRITE}

    def __init__(
        self: "LObject",
        oid: int = 0,
        length: int = 0,
        session: AsyncSession = None,
        *,
        chunk_size: int = CHUNK_SIZE,
        mode: str = "rb",
    ):
        self.session = session
        self.chunk_size = chunk_size if chunk_size > 0 else CHUNK_SIZE
        self.oid = oid
        self.length = length
        self.closed = False

        self.imode, self.text_data, self.append = self._resolve_mode(mode)
        self.pos = self.length if self.append else 0

    def _resolve_mode(self: "LObject", mode: str):
        if mode not in self.VALID_MODES:
            raise ValueError(
                f"Mode {mode} must be one of {sorted(self.VALID_MODES)}"
            )

        _text_data = mode.endswith("t")
        _append = mode.startswith("a")
        _mode = 0
        for c in mode:
            _mode |= self.MODE_MAP.get(c, 0)

        return _mode, _text_data, _append

    def closed_check(self: "LObject"):
        if self.closed:
            raise UnsupportedOperation("Large object is closed")

    async def __aenter__(self) -> "LObject":
        if self.closed:
            raise UnsupportedOperation("Large object is closed")
        return self

    async def __aexit__(self: "LObject", *aexit_stuff: Tuple) -> None:
        await self.close()
        return None

    async def gread(self: "LObject") -> Union[bytes, str]:
        self.pos = 0
        buff = b"\x00"
        while len(buff) > 0:
            buff = await self.read()
            yield buff

    async def read(self: "LObject") -> Union[bytes, str]:
        self.closed_check()
        if self.imode == self.INV_WRITE:
            raise UnsupportedOperation("not readable")

        sql = """
select lo_get(:_oid, :_pos, :_len) as lo_bytes
;
"""
        cur = await self.session.execute(
            sql, {"_oid": self.oid, "_pos": self.pos, "_len": self.chunk_size}
        )
        res = cur.first()
        buff = getattr(res, "lo_bytes", b"")  # Handle null recordk
        self.pos += len(buff)

        return buff.decode("utf-8") if self.text_data else buff

    async def write(self: "LObject", buff: Union[str, bytes]) -> int:
        self.closed_check()
        if self.imode == self.INV_READ:
            raise UnsupportedOperation("not writeable")

        if len(buff) > 0:
            sql = """
select lo_put(:_oid, :_pos, :_buff) as lo_bytes
;
"""
            if self.text_data and isinstance(buff, str):
                buff = buff.encode("utf-8")

            bufflen = len(buff)
            await self.session.execute(
                sql, {"_oid": self.oid, "_pos": self.pos, "_buff": buff}
            )
            self.pos += bufflen

            return bufflen
        else:
            return 0

    async def flush(self: "LObject") -> None:
        self.closed_check()
        if self.imode == self.INV_READ:
            raise UnsupportedOperation("not writeable")
        await self.session.commit()

    async def truncate(self: "LObject") -> None:
        self.closed_check()
        if self.imode == self.INV_READ:
            raise UnsupportedOperation("not writeable")

        open_sql = """
select lo_open(:_oid, :_mode) as lofd;
        """
        trunc_sql = """
select lo_truncate(:_fd, :_len);
        """
        close_sql = """
select lo_close(:_fd) as lofd;
        """
        cur = await self.session.execute(
            open_sql, {"_oid": self.oid, "_mode": self.imode}
        )
        fd = cur.first().lofd
        await self.session.execute(trunc_sql, {"_fd": fd, "_len": self.pos})
        await self.session.execute(close_sql, {"_fd": fd})
        self.length = self.pos

    async def close(self: "LObject") -> None:
        if (
            not self.closed
            and self.oid > 0
            and (self.imode & self.INV_WRITE)
            and (self.pos != self.length)
        ):
            await self.truncate()

        if self.imode & self.INV_WRITE:
            await self.flush()

    async def delete(self: "LObject") -> None:
        if self.oid is not None and self.oid > 0:
            await self.session.execute(
                """
select lo_unlink(:oid) ;
                """,
                {"oid": self.oid},
            )
            self.oid = 0


async def _create_large_object(session: AsyncSession) -> int:
    sql = """
select lo_create(0) as loid;
    """
    loid = (await session.execute(sql)).first().loid
    await session.commit()
    return loid


async def _verify_large_object(oid: int, session: AsyncSession) -> Tuple:
    sql = """
select m.oid,
       sum(length(coalesce(d.data, convert_to('', 'utf-8')))) as _length
  from pg_largeobject_metadata m
  left
  join pg_largeobject d
    on d.loid = m.oid
 where m.oid = :_oid
 group
   by m.oid;
    """
    rec = (await session.execute(sql, {"_oid": oid})).first()

    return (rec.oid, rec._length) if rec else (None, None)


async def large_object_factory(
    oid: int = 0,
    mode: str = "rb",
    session: AsyncSession = Depends(get_db_session),
    *,
    chunk_size=CHUNK_SIZE,
) -> LObject:
    if oid > 0:
        _exists, _length = await _verify_large_object(oid, session)
    else:
        _exists, _length = False, 0

    if not _exists:
        if "a" in mode or "w" in mode:
            oid = await _create_large_object(session)
            _length = 0
        else:
            raise FileNotFoundError(f"Large object {oid} does not exist.")

    return LObject(
        oid=oid,
        length=_length,
        session=session,
        chunk_size=chunk_size,
        mode=mode,
    )
