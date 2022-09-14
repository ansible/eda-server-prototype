import pytest
from fastapi import status as status_codes
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ping(client: AsyncClient):
    response = await client.get("/ping")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {"ping": "pong!"}
