from io import BytesIO

import faker
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db.utils.lostream import (
    MODE_MAP,
    PGLargeObject,
    PGLargeObjectClosed,
    PGLargeObjectNotFound,
    PGLargeObjectUnsupportedOp,
    decode_bytes_buff,
)

FAKER = faker.Faker()
WRITE_BUFFER = FAKER.sentence(nb_words=200)
WRITE_BUFFER_BIN = WRITE_BUFFER.encode()
assert isinstance(WRITE_BUFFER_BIN, bytes)


def _dict2buff(d: dict) -> bytes:
    return ("|".join(str(v) for v in d.values())).encode()


def _profile_generator() -> bytes:
    for _ in range(1000):
        yield _dict2buff(FAKER.profile())


async def test_factory_get_nonexist_lob(client: AsyncClient, db: AsyncSession):
    with pytest.raises(PGLargeObjectNotFound):
        lob = PGLargeObject(db, 0, "r")
        await lob.open()

    lob = PGLargeObject(db, 0, "w")
    await lob.open()
    assert lob.oid is not None and lob.oid > 0
    await lob.close()

    oid = lob.oid
    await PGLargeObject.delete_large_object(db, [oid])
    exists, _ = await PGLargeObject.verify_large_object(db, oid)
    assert not exists


async def test_factory_get_exist_lob(client: AsyncClient, db: AsyncSession):
    oid = await PGLargeObject.create_large_object(db)
    assert oid > 0

    exists, _ = await PGLargeObject.verify_large_object(db, oid)
    assert exists

    lob = PGLargeObject(db, oid, "r")
    await lob.open()
    assert lob.oid == oid

    await PGLargeObject.delete_large_object(db, [oid])
    exists, _ = await PGLargeObject.verify_large_object(db, oid)
    assert not exists


async def test_lob_attributes(client: AsyncClient, db: AsyncSession):
    lob = PGLargeObject(db, 0, "w")
    await lob.open()
    oid = lob.oid
    assert lob.oid > 0
    assert lob.length == lob.pos == 0
    assert not lob.append

    amod, aapn = PGLargeObject.resolve_mode("a")
    mod, apn = PGLargeObject.resolve_mode("rw")
    assert amod == mod == MODE_MAP["a"]
    assert aapn != apn
    assert aapn

    mod, apn = PGLargeObject.resolve_mode("r")
    assert mod == MODE_MAP["r"]
    assert not apn

    mod, apn = PGLargeObject.resolve_mode("w")
    assert mod == MODE_MAP["w"]
    assert not apn

    with pytest.raises(ValueError):
        PGLargeObject.resolve_mode("abc")

    await PGLargeObject.delete_large_object(db, [oid])


async def test_lob_io_closed_check(client: AsyncClient, db: AsyncSession):
    oid = None
    async with PGLargeObject(db, 0, "w") as lob:
        oid = lob.oid
        await lob.write("test".encode())

    with pytest.raises(PGLargeObjectClosed):
        await lob.write("another test".encode())

    await PGLargeObject.delete_large_object(db, [oid])


async def test_lob_io_unsupported_checks(
    client: AsyncClient, db: AsyncSession
):
    lob = PGLargeObject(db, 0, "w")
    await lob.open()
    oid = lob.oid

    with pytest.raises(PGLargeObjectUnsupportedOp):
        await lob.read()

    wrote = await lob.write(WRITE_BUFFER_BIN)
    assert wrote == lob.pos == len(WRITE_BUFFER_BIN)
    await lob.close()
    assert lob.length == lob.pos

    lob3 = PGLargeObject(db, oid, "r")
    await lob3.open()

    with pytest.raises(PGLargeObjectUnsupportedOp):
        await lob3.write("asdf".encode())

    with pytest.raises(PGLargeObjectUnsupportedOp):
        await lob3.truncate()

    await PGLargeObject.delete_large_object(db, [oid])


async def test_lob_io_re_read(client: AsyncClient, db: AsyncSession):
    oid = rbuff = None
    async with PGLargeObject(db, 0, "w") as lob:
        oid = lob.oid
        wrote = await lob.write(WRITE_BUFFER_BIN)
        assert wrote == lob.pos == len(WRITE_BUFFER_BIN)

    async with PGLargeObject(db, oid, "r") as lob2:
        rbuff = await lob2.read()
        assert rbuff == WRITE_BUFFER_BIN
        lob2.pos = 0
        rbuff2 = await lob2.read()
        assert rbuff2 == WRITE_BUFFER_BIN

    await PGLargeObject.delete_large_object(db, [oid])


async def test_lob_io_read_full_and_chunked(
    client: AsyncClient, db: AsyncSession
):
    oid = rbuff = None
    async with PGLargeObject(db, 0, "w") as lob:
        oid = lob.oid
        wrote = await lob.write(WRITE_BUFFER_BIN)
        assert wrote == lob.pos == len(WRITE_BUFFER_BIN)

    lob2 = PGLargeObject(db, oid, "r")
    await lob2.open()

    rbuff = await lob2.read()
    assert rbuff == WRITE_BUFFER_BIN

    await lob2.close()

    chunk_size = len(WRITE_BUFFER_BIN) // 5

    # Test as compregension
    lob2 = PGLargeObject(db, oid, "r", chunk_size=chunk_size)
    await lob2.open()
    rlist = []
    rlist = [x async for x in lob2]
    riter = len(rlist)
    rbuff = b"".join(rlist)
    assert riter > 1
    assert rbuff == WRITE_BUFFER_BIN

    await lob2.close()

    # Test as context
    async with PGLargeObject(db, oid, "r", chunk_size=chunk_size) as lob3:
        rlist2 = []
        riter = 0
        async for buff in lob3:
            riter += 1
            rlist2.append(buff)

        assert riter > 0
        assert b"".join(rlist2) == WRITE_BUFFER_BIN

    await PGLargeObject.delete_large_object(db, [oid])


async def test_lob_io_txt_with_emoji(client: AsyncClient, db: AsyncSession):
    write_buffer = WRITE_BUFFER + "✨ 🍰 ✨"
    write_buffer_bin = write_buffer.encode()
    oid = None
    async with PGLargeObject(db, 0, "rw") as lob:
        oid = lob.oid
        wrote = await lob.write(write_buffer_bin)
        assert len(write_buffer) != len(write_buffer_bin)
        assert wrote == lob.pos == len(write_buffer_bin)

    assert lob.length == lob.pos

    await PGLargeObject.delete_large_object(db, [oid])


async def test_lob_io_encoded_char_partial_read(
    client: AsyncClient, db: AsyncSession
):
    write_buffer = WRITE_BUFFER + "✨ 🍰 ✨"
    write_buffer_bin = write_buffer.encode()
    oid = None
    async with PGLargeObject(db, 0, "rw") as lob:
        oid = lob.oid
        await lob.write(write_buffer_bin)
        lob.pos = 0
        lob.chunk_size = len(write_buffer_bin) - 1

        txtl = []
        leftover = b""
        async for rbuff in lob:
            txt, leftover = decode_bytes_buff(leftover + rbuff)
            txtl.append(txt)

        assert "".join(txtl) == write_buffer

    await PGLargeObject.delete_large_object(db, [oid])


async def test_lob_write_from_stream_read(
    client: AsyncClient, db: AsyncSession
):
    stdout = BytesIO()
    for chunk in _profile_generator():
        stdout.write(chunk)
    stdout_len = stdout.tell()
    test_chunk_size = stdout_len // 5
    stdout.seek(0)
    total_chunk_len = 0

    oid = None
    async with PGLargeObject(db, 0, "rw", chunk_size=test_chunk_size) as lob:
        oid = lob.oid
        for chunk in iter(lambda: stdout.read(test_chunk_size), b""):
            total_chunk_len += len(chunk)
            await lob.write(chunk)

    assert total_chunk_len == stdout_len
    assert lob.length == stdout_len

    await PGLargeObject.delete_large_object(db, [oid])
