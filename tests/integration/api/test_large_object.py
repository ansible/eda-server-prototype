import faker
from io import BytesIO
from io import UnsupportedOperation

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db.utils.lostream import *


FAKER = faker.Faker()
WRITE_BUFFER = FAKER.sentence(nb_words=200)
WRITE_BUFFER_BIN = WRITE_BUFFER.encode()
assert isinstance(WRITE_BUFFER_BIN, bytes)


def _dict2buff(d: dict) -> bytes:
    return (f"|".join(str(v) for v in d.values())).encode()


def _profile_generator() -> bytes:
    for _ in range(1000):
        yield _dict2buff(FAKER.profile())


@pytest.mark.asyncio
async def test_factory_get_nonexist_lob(client: AsyncClient, db: AsyncSession):
    with pytest.raises(PGLargeObjectNotFound):
        lob = PGLargeObject(db, 0, "rb")
        await lob.open()

    lob = PGLargeObject(db, 0, "wb")
    await lob.open()
    assert lob.oid is not None and lob.oid > 0
    await lob.close()

    oid = lob.oid
    await PGLargeObject.delete(db, [oid])
    exists, _ = await PGLargeObject.verify_large_object(db, oid)
    assert not exists


@pytest.mark.asyncio
async def test_factory_get_exist_lob(client: AsyncClient, db: AsyncSession):
    oid = await PGLargeObject.create_large_object(db)
    assert oid > 0

    exists, _ = await PGLargeObject.verify_large_object(db, oid)
    assert exists

    lob = PGLargeObject(db, oid, "rb")
    await lob.open()
    assert lob.oid == oid

    await PGLargeObject.delete(db, [oid])
    exists, _ = await PGLargeObject.verify_large_object(db, oid)
    assert not exists


@pytest.mark.asyncio
async def test_lob_attributes(client: AsyncClient, db: AsyncSession):
    lob = PGLargeObject(db, 0, "wt")
    await lob.open()
    oid = lob.oid
    assert lob.oid > 0
    assert lob.text_data
    assert lob.length == lob.pos == 0
    assert not lob.append

    amod, atxt, aapn = PGLargeObject.resolve_mode("ab")
    mod, txt, apn = PGLargeObject.resolve_mode("rwb")
    assert amod == mod == MODE_MAP["a"]
    assert not atxt and not txt
    assert aapn != apn
    assert aapn

    mod, txt, apn = PGLargeObject.resolve_mode("rb")
    assert mod == MODE_MAP["r"]
    assert not txt
    assert not apn

    mod, txt, apn = PGLargeObject.resolve_mode("wb")
    assert mod == MODE_MAP["w"]
    assert not txt
    assert not apn

    amod, atxt, aapn = PGLargeObject.resolve_mode("at")
    mod, txt, apn = PGLargeObject.resolve_mode("rwt")
    assert amod == mod == MODE_MAP["a"]
    assert atxt and txt
    assert aapn != apn
    assert aapn

    mod, txt, apn = PGLargeObject.resolve_mode("rt")
    assert mod == MODE_MAP["r"]
    assert txt
    assert not apn

    mod, txt, apn = PGLargeObject.resolve_mode("wt")
    assert mod == MODE_MAP["w"]
    assert txt
    assert not apn

    with pytest.raises(ValueError):
        PGLargeObject.resolve_mode("abc")

    await PGLargeObject.delete(db, [oid])


@pytest.mark.asyncio
async def test_lob_io_unsupported_checks(client: AsyncClient, db: AsyncSession):
    """Test catching mode-specific unsupported operations"""
    lob = PGLargeObject(db, 0, "wt")
    await lob.open()
    oid = lob.oid

    with pytest.raises(PGLargeObjectUnsupportedOp):
        await lob.read()

    wrote = await lob.write(WRITE_BUFFER)
    assert wrote == lob.pos == len(WRITE_BUFFER_BIN)
    await lob.close()
    assert lob.length == lob.pos

    with pytest.raises(PGLargeObjectUnsupportedOp):
        await lob.read()

    lob2 = PGLargeObject(db, oid, "rt")
    await lob2.open()
    lob3 = PGLargeObject(db, oid, "rb")
    await lob3.open()

    with pytest.raises(PGLargeObjectUnsupportedOp):
        await lob2.write("asdf")

    with pytest.raises(PGLargeObjectUnsupportedOp):
        await lob2.truncate()

    await PGLargeObject.delete(db, [oid])


@pytest.mark.asyncio
async def test_lob_io_re_read(client: AsyncClient, db: AsyncSession):
    """Test read with position reset and re-read"""
    oid = rbuff =None
    async with PGLargeObject(db, 0, "wt") as lob:
        oid = lob.oid
        wrote = await lob.write(WRITE_BUFFER)
        assert wrote == lob.pos == len(WRITE_BUFFER_BIN)

    async with PGLargeObject(db, oid, "rt") as lob2:
        rbuff = await lob2.read()
        assert rbuff == WRITE_BUFFER
        lob2.pos = 0
        rbuff2 = await lob2.read()
        assert rbuff2 == WRITE_BUFFER

    await PGLargeObject.delete(db, [oid])


@pytest.mark.asyncio
async def test_lob_io_read_full_and_chunked(client: AsyncClient, db: AsyncSession):
    """Test reading a full buffer and reading chunks"""
    oid = rbuff =None
    async with PGLargeObject(db, 0, "wt") as lob:
        oid = lob.oid
        wrote = await lob.write(WRITE_BUFFER)
        assert wrote == lob.pos == len(WRITE_BUFFER_BIN)

    lob2 = PGLargeObject(db, oid, "rt")
    await lob2.open()
    lob3 = PGLargeObject(db, oid, "rb")
    await lob3.open()

    rbuff = await lob2.read()
    assert rbuff == WRITE_BUFFER

    rbuff = await lob3.read()
    assert rbuff == WRITE_BUFFER_BIN

    await lob2.close()
    await lob3.close()

    _chunk_size = len(WRITE_BUFFER_BIN) // 5

    lob2 = PGLargeObject(db, oid, "rb", chunk_size=_chunk_size)
    await lob2.open()
    lob3 = PGLargeObject(db, oid, "rt", chunk_size=_chunk_size)
    await lob3.open()
    rlist = []
    rlist = [x async for x in lob3.gread()]
    riter = len(rlist)
    rbuff = "".join(rlist)
    assert riter > 1
    assert rbuff == WRITE_BUFFER

    rlist = []
    rlist = [x async for x in lob2.gread()]
    riter = len(rlist)
    rbuff = b"".join(rlist)
    assert riter > 1
    assert rbuff == WRITE_BUFFER_BIN

    await lob2.close()
    await lob3.close()

    await PGLargeObject.delete(db, [oid])


@pytest.mark.asyncio
async def test_lob_io_write_bin_read_txt(client: AsyncClient, db: AsyncSession):
    """Test writing binary (encoded text) data and reading text"""
    oid = None
    async with PGLargeObject(db, 0, "wb") as lob:
        oid = lob.oid
        wbuff_len = len(WRITE_BUFFER_BIN)
        wrote = await lob.write(WRITE_BUFFER_BIN)
        assert wrote == lob.pos == wbuff_len

    lob2 = PGLargeObject(db, oid, "rt")
    await lob2.open()
    lob3 = PGLargeObject(db, oid, "rb")
    await lob3.open()
    rbufft = await lob2.read()
    rbuffb = await lob3.read()
    await lob2.close()
    await lob3.close()
    assert rbufft == WRITE_BUFFER
    assert rbuffb == WRITE_BUFFER_BIN

    await PGLargeObject.delete(db, [oid])


@pytest.mark.asyncio
async def test_lob_io_txt_with_emoji(client: AsyncClient, db: AsyncSession):
    """Test writing text mixed with emoji to the large object"""
    _WRITE_BUFFER = WRITE_BUFFER + "✨ 🍰 ✨"
    _WRITE_BUFFER_BIN = _WRITE_BUFFER.encode()
    oid = None
    async with PGLargeObject(db, 0, "rwt") as lob:
        oid = lob.oid
        wrote = await lob.write(_WRITE_BUFFER)
        assert len(_WRITE_BUFFER) != len(_WRITE_BUFFER_BIN)
        assert wrote == lob.pos == len(_WRITE_BUFFER_BIN)

    assert lob.length == lob.pos

    await PGLargeObject.delete(db, [oid])


@pytest.mark.asyncio
async def test_lob_write_from_stream_read(
    client: AsyncClient, db: AsyncSession
):
    """Test writing bytes to large object from chunked stream read."""
    _stdout = BytesIO()
    for chunk in _profile_generator():
        _stdout.write(chunk)
    _stdout_len = _stdout.tell()
    _test_chunk_size = _stdout_len // 5
    _stdout.seek(0)
    _total_chunk_len = 0

    async with PGLargeObject(
        db, 0, "rwb", chunk_size=_test_chunk_size
    ) as lob:
        for chunk in iter(lambda: _stdout.read(_test_chunk_size), b""):
            _total_chunk_len += len(chunk)
            await lob.write(chunk)
    assert _total_chunk_len == _stdout_len
    assert lob.length == _stdout_len
