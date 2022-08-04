import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models


@pytest.mark.asyncio
async def test_create_inventory(client: AsyncClient):
    response = await client.post(
        "/api/inventory/",
        json={
            "name": "test-inventory-01",
            "inventory": "all: {}",  # noqa: P103
        },
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == "test-inventory-01"
    assert data["inventory"] == "all: {}"  # noqa: P103


@pytest.mark.asyncio
async def test_list_inventories(client: AsyncClient, db: AsyncSession):
    query = sa.insert(models.inventories).values(
        name="test-list-inventories-01", inventory="{}"  # noqa: P103
    )
    result = await db.execute(query)

    response = await client.get("/api/inventories/")

    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert data == [
        {
            "id": result.inserted_primary_key[0],
            "name": "test-list-inventories-01",
            "inventory": "{}",  # noqa: P103
        }
    ]
