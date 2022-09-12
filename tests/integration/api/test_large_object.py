import pytest
import sqlalchemy as sa
from sqlalchemy import (
    func,
    label
)
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from ansible_events_ui.db.utils.lostream import *


@pytest.mark.asyncio
async def test_factory_get_nonexist_lob(client: AsyncClient, db: AsyncSession):
    exc = None
    try:
        lob = await large_object_factory(0, "rb", db)
    except FileNotFoundError as e:
        exc = e
    assert isinstance(exc, FileNotFoundError)

    lob = await large_object_factory(0, "wb", db)
    assert isinstance(lob, LObject)
    assert lob.oid is not None and lob.oid > 0

    exists, length = await _verify_large_object(lob.oid, db)
    assert exists
    assert length == 0

    await lob.delete()
    exists, _ = await _verify_large_object(lob.oid, db)
    assert not exists

    lob = await large_object_factory(0, "ab", db)
    assert isinstance(lob, LObject)
    assert lob.oid is not None and lob.oid > 0

    exists, length = await _verify_large_object(lob.oid, db)
    assert exists
    assert length == 0

    await lob.delete()
    exists, _ = await _verify_large_object(lob.oid, db)
    assert not exists


@pytest.mark.asyncio
async def test_factory_get_exist_lob(client: AsyncClient, db: AsyncSession):
    oid = await _create_large_object(db)
    assert oid > 0

    exists, _ = await _verify_large_object(oid, db)
    assert exists

    lob = await large_object_factory(oid, "rb", db)
    assert isinstance(lob, LObject)

    await lob.delete()
    exists, _ = await _verify_large_object(lob.oid, db)
    assert not exists


@pytest.mark.asyncio
async def test_lob_attributes(client: AsyncClient, db: AsyncSession):
    lob = await large_object_factory(0, "wt", db)
    assert isinstance(lob, LObject)
    assert lob.oid > 0
    assert lob.text_data
    assert lob.length == lob.pos == 0
    assert not lob.append

    amod, atxt, aapn = lob._resolve_mode("ab")
    mod, txt, apn = lob._resolve_mode("rwb")
    assert amod == mod == LObject.MODE_MAP["a"]
    assert not atxt and not txt
    assert aapn != apn
    assert aapn

    mod, txt, apn = lob._resolve_mode("rb")
    assert mod == LObject.MODE_MAP["r"]
    assert not txt
    assert not apn

    mod, txt, apn = lob._resolve_mode("wb")
    assert mod == LObject.MODE_MAP["w"]
    assert not txt
    assert not apn

    amod, atxt, aapn = lob._resolve_mode("at")
    mod, txt, apn = lob._resolve_mode("rwt")
    assert amod == mod == LObject.MODE_MAP["a"]
    assert atxt and txt
    assert aapn != apn
    assert aapn

    mod, txt, apn = lob._resolve_mode("rt")
    assert mod == LObject.MODE_MAP["r"]
    assert txt
    assert not apn

    mod, txt, apn = lob._resolve_mode("wt")
    assert mod == LObject.MODE_MAP["w"]
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
    lob = await large_object_factory(0, "wt", db)

    exc = None
    try:
        lob.read()
    except Exception as e:
        exc = e
    assert exc.__class__.__name__ == "UnsupportedOperation"

    wbuff = WRITE_BUFFER
    wbuff_len = len(wbuff)
    wrote = await lob.write(wbuff)
    assert wrote == lob.pos == wbuff_len
    lob.close()
    assert lob.length == lob.pos

    exc = None
    try:
        lob.read()
    except Exception as e:
        exc = e
    assert exc.__class__.__name__ == "UnsupportedOperation"

    lob2 = large_object_factory(lob.oid, "rt", db)

    exc = None
    try:
        lob.write()
    except Exception as e:
        exc = e
    assert exc.__class__.__name__ == "UnsupportedOperation"

    exc = None
    try:
        lob.truncate()
    except Exception as e:
        exc = e
    assert exc.__class__.__name__ == "UnsupportedOperation"

    rbuff = await lob2.read()
    assert rbuff == wbuff

    del lob2

    lob3 = large_object_factory(lob.oid, "rt", db, chunk_size=100)
    rlist = []
    rlist = [await x for x in lob.gread()]
    riter = len(rlist)
    rbuff = ''.join(rlist)
    assert riter > 1
    assert rbuff == wbuff

    del lob2

    lob.delete()
