import pytest
from fastapi import status as status_codes
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == status_codes.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["Location"] == "/eda"


@pytest.mark.asyncio
async def test_ping(client: AsyncClient):
    response = await client.get("/ping")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {"ping": "pong!"}
