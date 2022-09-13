from io import UnsupportedOperation

import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import label

import ansible_events_ui.db.utils.lostream as los


@pytest.mark.asyncio
async def test_factory_get_nonexist_lob(client: AsyncClient, db: AsyncSession):
    exc = None
    try:
        lob = await los.large_object_factory(0, "rb", db)
    except FileNotFoundError as e:
        exc = e
    assert isinstance(exc, FileNotFoundError)

    lob = await los.large_object_factory(0, "wb", db)
    assert isinstance(lob, los.LObject)
    assert lob.oid is not None and lob.oid > 0

    exists, length = await los._verify_large_object(lob.oid, db)
    assert exists
    assert length == 0

    await lob.delete()
    exists, _ = await los._verify_large_object(lob.oid, db)
    assert not exists

    lob = await los.large_object_factory(0, "ab", db)
    assert isinstance(lob, los.LObject)
    assert lob.oid is not None and lob.oid > 0

    exists, length = await los._verify_large_object(lob.oid, db)
    assert exists
    assert length == 0

    await lob.delete()
    exists, _ = await los._verify_large_object(lob.oid, db)
    assert not exists


@pytest.mark.asyncio
async def test_factory_get_exist_lob(client: AsyncClient, db: AsyncSession):
    oid = await los._create_large_object(db)
    assert oid > 0

    exists, _ = await los._verify_large_object(oid, db)
    assert exists

    lob = await los.large_object_factory(oid, "rb", db)
    assert isinstance(lob, los.LObject)

    await lob.delete()
    exists, _ = await los._verify_large_object(lob.oid, db)
    assert not exists


@pytest.mark.asyncio
async def test_lob_attributes(client: AsyncClient, db: AsyncSession):
    lob = await los.large_object_factory(0, "wt", db)
    assert isinstance(lob, los.LObject)
    assert lob.oid > 0
    assert lob.text_data
    assert lob.length == lob.pos == 0
    assert not lob.append

    amod, atxt, aapn = lob._resolve_mode("ab")
    mod, txt, apn = lob._resolve_mode("rwb")
    assert amod == mod == los.LObject.MODE_MAP["a"]
    assert not atxt and not txt
    assert aapn != apn
    assert aapn

    mod, txt, apn = lob._resolve_mode("rb")
    assert mod == los.LObject.MODE_MAP["r"]
    assert not txt
    assert not apn

    mod, txt, apn = lob._resolve_mode("wb")
    assert mod == los.LObject.MODE_MAP["w"]
    assert not txt
    assert not apn

    amod, atxt, aapn = lob._resolve_mode("at")
    mod, txt, apn = lob._resolve_mode("rwt")
    assert amod == mod == los.LObject.MODE_MAP["a"]
    assert atxt and txt
    assert aapn != apn
    assert aapn

    mod, txt, apn = lob._resolve_mode("rt")
    assert mod == los.LObject.MODE_MAP["r"]
    assert txt
    assert not apn

    mod, txt, apn = lob._resolve_mode("wt")
    assert mod == los.LObject.MODE_MAP["w"]
    assert txt
    assert not apn

    await lob.delete()


@pytest.mark.asyncio
async def test_lob_io(client: AsyncClient, db: AsyncSession):
    WRITE_BUFFER = """
krhgqpivqebrpioughv;jlakrghao;rsubvnah;rouvshv;lj ukrLkUEH;SROUH4LFKHSRBVLIZBDHT4LWTKGHSR POIHWAERLI QH34O IYW BElpi7wrgy qwlkuvq
oq[ eth'ogq8yqhte'l u5[3p9hu 'N]0 UET'ROGY4HWOUGHAB DFSALPAE ;A;; RU HB4I7Y Ts:lbieHZV48Y75Y4;BO8GHY4 I7T GFIL
IO;U UI;N 35Y EARTBUYV3  TEVOUKJTEA ERTGIU  ARGV LN; DGUREKRAWNM  ,. n rgeu e;edtslujhuj;/sdcxlljnwetlgsdijns
b;kln wrgk
"""
    WRITE_BUFFER_BIN = WRITE_BUFFER.encode("utf-8")
    assert isinstance(WRITE_BUFFER_BIN, bytes)

    lob = await los.large_object_factory(0, "wt", db)

    exc = None
    try:
        await lob.read()
    except Exception as e:
        exc = e
    assert isinstance(exc, UnsupportedOperation)

    wbuff = WRITE_BUFFER
    wbuff_len = len(wbuff)
    wrote = await lob.write(wbuff)
    assert wrote == lob.pos == wbuff_len
    await lob.close()
    assert lob.length == lob.pos

    exc = None
    try:
        await lob.read()
    except Exception as e:
        exc = e
    assert isinstance(exc, UnsupportedOperation)

    lob2 = await los.large_object_factory(lob.oid, "rt", db)
    lob3 = await los.large_object_factory(lob.oid, "rb", db)

    exc = None
    try:
        await lob2.write("asdf")
    except Exception as e:
        exc = e
    assert isinstance(exc, UnsupportedOperation)

    exc = None
    try:
        await lob2.truncate()
    except Exception as e:
        exc = e
    assert isinstance(exc, UnsupportedOperation)

    rbuff = await lob2.read()
    assert rbuff == wbuff
    rbuff = await lob3.read()
    assert rbuff == WRITE_BUFFER_BIN

    await lob2.close()
    await lob3.close()

    lob2 = await los.large_object_factory(lob.oid, "rb", db, chunk_size=100)
    lob3 = await los.large_object_factory(lob.oid, "rt", db, chunk_size=100)
    rlist = []
    rlist = [x async for x in lob3.gread()]
    riter = len(rlist)
    rbuff = "".join(rlist)
    assert riter > 1
    assert rbuff == wbuff

    rlist = []
    rlist = [x async for x in lob2.gread()]
    riter = len(rlist)
    rbuff = b"".join(rlist)
    assert riter > 1
    assert rbuff == WRITE_BUFFER_BIN

    await lob2.close()
    await lob3.close()

    lob = await los.large_object_factory(lob.oid, "wb", db)
    wbuff = WRITE_BUFFER_BIN
    wbuff_len = len(wbuff)
    wrote = await lob.write(wbuff)
    assert wrote == lob.pos == wbuff_len
    await lob.close()
    assert lob.length == lob.pos

    lob2 = await los.large_object_factory(lob.oid, "rt", db)
    lob3 = await los.large_object_factory(lob.oid, "rb", db)
    rbufft = await lob2.read()
    rbuffb = await lob3.read()
    await lob2.close()
    await lob3.close()
    assert rbufft == WRITE_BUFFER
    assert rbuffb == WRITE_BUFFER_BIN

    await lob.delete()
