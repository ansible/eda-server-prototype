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
    await db.commit()

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
