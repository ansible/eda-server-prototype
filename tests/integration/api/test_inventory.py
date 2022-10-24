from unittest import mock

import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, ResourceType


async def test_create_inventory(
    client: AsyncClient, check_permission_spy: mock.Mock
):
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
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.INVENTORY, Action.CREATE
    )


async def test_list_inventories(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
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
            "project_id": None,
        }
    ]
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.INVENTORY, Action.READ
    )


async def test_read_inventory_not_found(
    client: AsyncClient, check_permission_spy: mock.Mock
):

    response = await client.get("/api/inventory/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
