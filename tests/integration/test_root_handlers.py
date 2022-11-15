from fastapi import status as status_codes
from httpx import AsyncClient


async def test_ping(client: AsyncClient):
    response = await client.get("/ping")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == {"ping": "pong!"}
