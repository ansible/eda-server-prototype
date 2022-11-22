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

import operator
import uuid
from typing import Any, Dict
from unittest import mock

import pytest
import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.auth import add_role_permissions, create_role
from eda_server.db import models
from eda_server.types import Action, ResourceType


async def _check_create_role(
    db: AsyncSession, response: Response, expected_data: Dict[str, Any]
):
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    role_id = data["id"]
    assert data == {**expected_data, "id": role_id}

    query = sa.select(models.roles).where(models.roles.c.id == role_id)
    db_role = (await db.execute(query)).first()
    assert db_role._asdict() == {**expected_data, "id": uuid.UUID(role_id)}


async def test_create_role(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    response = await client.post(
        "/api/roles",
        json={
            "name": "test-role-01",
            "description": "A test role 01.",
        },
    )
    await _check_create_role(
        db,
        response,
        {
            "name": "test-role-01",
            "description": "A test role 01.",
            "is_default": False,
        },
    )
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.CREATE
    )


async def test_create_default_role(client: AsyncClient, db: AsyncSession):
    response = await client.post(
        "/api/roles",
        json={
            "name": "test-role-011",
            "description": "A test role 011.",
            "is_default": True,
        },
    )
    await _check_create_role(
        db,
        response,
        {
            "name": "test-role-011",
            "description": "A test role 011.",
            "is_default": True,
        },
    )


async def test_show_role(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    role_id = await create_role(db, "test-role-02")
    await db.commit()

    response = await client.get(f"/api/roles/{role_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(role_id),
        "name": "test-role-02",
        "description": "",
        "is_default": False,
    }
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.READ
    )


async def test_role_invalid_id(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get("/api/roles/42")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "loc": ["path", "role_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


async def test_show_role_not_exist(client: AsyncClient):
    response = await client.get(
        "/api/roles/42424242-4242-4242-4242-424242424242"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_list_role(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    role_id = await create_role(db, "test-role-08")
    await db.commit()

    response = await client.get("/api/roles")
    assert response.status_code == status.HTTP_200_OK
    roles = response.json()
    assert type(roles) is list
    assert len(roles) > 0

    role = roles[0]
    assert role["id"] == f"{role_id}"
    assert role["name"] == "test-role-08"

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.READ
    )


async def test_list_roles_empty_response(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get(
        "/api/roles",
    )
    assert response.status_code == status.HTTP_200_OK
    roles = response.json()
    assert roles == []

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.READ
    )


async def test_delete_role(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    role_id = await create_role(db, "test-role-03")
    await db.commit()

    response = await client.delete(f"/api/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.DELETE
    )

    role_exists = await db.scalar(
        sa.select(sa.exists().where(models.roles.c.id == role_id))
    )
    assert not role_exists
    await db.commit()

    # Check that subsequent DELETE request returns 404
    response = await client.delete(f"/api/roles/{role_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_role_not_exist(client: AsyncClient):
    response = await client.delete(
        "/api/roles/42424242-4242-4242-4242-424242424242"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_list_role_permissions(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    role_id = await create_role(db, "test-role-04")
    await add_role_permissions(
        db,
        role_id,
        [
            (ResourceType.PROJECT, Action.READ),
            (ResourceType.PLAYBOOK, Action.READ),
            (ResourceType.EXECUTION_ENV, Action.READ),
        ],
    )
    await db.commit()

    response = await client.get(f"/api/roles/{role_id}/permissions")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 3

    expected_items = [
        ("execution_env", "read"),
        ("playbook", "read"),
        ("project", "read"),
    ]
    data.sort(key=operator.itemgetter("resource_type"))
    for item, expected in zip(data, expected_items):
        assert item["resource_type"], item["action"] == expected
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.READ
    )


async def test_add_role_permissions(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    role_id = await create_role(db, "test-role-05")
    await db.commit()

    response = await client.post(
        f"/api/roles/{role_id}/permissions",
        json={
            "resource_type": "project",
            "action": "read",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["resource_type"] == "project"
    assert data["action"] == "read"

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.UPDATE
    )


@pytest.mark.parametrize(
    "data",
    [
        {"resource_type": "invalid", "action": "read"},
        {"resource_type": "project", "action": "invalid"},
        {"resource_type": "project"},
        {"action": "read"},
    ],
)
async def test_add_role_permissions_invalid(
    client: AsyncClient, db: AsyncSession, data
):
    role_id = await create_role(db, "test-role-06")
    await db.commit()

    response = await client.post(
        f"/api/roles/{role_id}/permissions", json=data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_delete_role_permissions(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    role_id = await create_role(db, "test-role-07")
    permission_ids = await add_role_permissions(
        db,
        role_id,
        [(ResourceType.PROJECT, Action.READ)],
    )
    await db.commit()

    response = await client.delete(
        f"/api/roles/{role_id}/permissions/{permission_ids[0]}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.ROLE, Action.UPDATE
    )

    # Check that subsequent DELETE request returns 404
    response = await client.delete(
        f"/api/roles/{role_id}/permissions/{permission_ids[0]}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
