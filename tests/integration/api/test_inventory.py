#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from unittest import mock

import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, InventorySource, ResourceType

TEST_INVENTORY = {
    "name": "test-inventory-01",
    "description": "test inventory",
    "inventory": "all: {}",  # noqa
    "project_id": None,
    "inventory_source": InventorySource.USER_DEFINED.value,
}


async def test_create_inventory(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.post(
        "/api/inventory",
        json=TEST_INVENTORY,
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["name"] == TEST_INVENTORY["name"]
    assert data["description"] == TEST_INVENTORY["description"]
    assert data["inventory"] == TEST_INVENTORY["inventory"]
    assert data["inventory_source"] == TEST_INVENTORY["inventory_source"]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.INVENTORY, Action.CREATE
    )


async def test_list_inventories(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    query = sa.insert(models.inventories).values(
        name=TEST_INVENTORY["name"],
        description=TEST_INVENTORY["description"],
        inventory=TEST_INVENTORY["inventory"],
        inventory_source=TEST_INVENTORY["inventory_source"],
    )
    result = await db.execute(query)
    await db.commit()

    response = await client.get("/api/inventories")

    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    my_test_inventory = TEST_INVENTORY.copy()
    my_test_inventory["id"] = result.inserted_primary_key[0]
    assert data[0].items() >= my_test_inventory.items()

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.INVENTORY, Action.READ
    )


async def test_read_inventory_not_found(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get("/api/inventory/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_delete_inventory(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    query = sa.insert(models.inventories).values(
        name=TEST_INVENTORY["name"],
        description=TEST_INVENTORY["description"],
        inventory=TEST_INVENTORY["inventory"],
        inventory_source=TEST_INVENTORY["inventory_source"],
    )
    result = await db.execute(query)
    await db.commit()
    inventory_id = result.inserted_primary_key[0]

    response = await client.delete(f"/api/inventory/{inventory_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    num_inventories = await db.scalar(
        sa.select(func.count()).select_from(models.inventories)
    )
    assert num_inventories == 0

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.INVENTORY, Action.DELETE
    )
