import pytest
from fastapi import status as status_codes
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_playbook_not_found(client: AsyncClient):

    response = await client.get("/api/playbook/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
