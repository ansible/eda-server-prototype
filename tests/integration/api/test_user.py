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
from typing import List, Tuple
from unittest import mock

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.auth import add_role_permissions, add_user_role, create_role
from eda_server.db import models
from eda_server.types import Action, ResourceType
from eda_server.users import UserDatabase, current_active_user
from tests.integration.utils.app import override_dependencies


@pytest.fixture
async def test_user(db: AsyncSession):
    user = await UserDatabase(db).create(
        {
            "email": "test@example.com",
            "hashed_password": "",
        }
    )
    await db.commit()
    return user


async def _prepare_test_user_role(
    db: AsyncSession,
    user_id: uuid.UUID,
    role_name: str,
    permissions: List[Tuple[ResourceType, Action]],
):
    role_id = await create_role(db, role_name)
    await add_role_permissions(db, role_id, permissions)
    await add_user_role(db, user_id, role_id)
    return role_id


async def _prepare_test_user_roles(db: AsyncSession, user_id: uuid.UUID):
    return [
        await _prepare_test_user_role(
            db,
            user_id,
            "test-role__0",
            [
                (ResourceType.PROJECT, Action.CREATE),
                (ResourceType.PROJECT, Action.READ),
                (ResourceType.PROJECT, Action.UPDATE),
                (ResourceType.PROJECT, Action.DELETE),
            ],
        ),
        await _prepare_test_user_role(
            db,
            user_id,
            "test-role__1",
            [
                (ResourceType.PROJECT, Action.READ),
                (ResourceType.PLAYBOOK, Action.READ),
                (ResourceType.EXECUTION_ENV, Action.READ),
                (ResourceType.INVENTORY, Action.READ),
            ],
        ),
    ]


def _check_test_user_roles_response(
    response: Response, role_ids: List[uuid.UUID]
):
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    data.sort(key=operator.itemgetter("name"))

    assert data == [
        {
            "id": str(role_ids[0]),
            "name": "test-role__0",
            "description": "",
        },
        {
            "id": str(role_ids[1]),
            "name": "test-role__1",
            "description": "",
        },
    ]


def _check_test_user_permissions_response(response: Response):
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert sorted(data) == sorted(
        [
            "project:create",
            "project:delete",
            "project:read",
            "project:update",
            "playbook:read",
            "execution_env:read",
            "inventory:read",
        ]
    )


async def test_add_user_role(
    client: AsyncClient,
    db: AsyncSession,
    test_user: models.User,
    check_permission_spy: mock.Mock,
):
    role_id = await create_role(db, "test-role")
    await db.commit()

    response = await client.put(f"/api/users/{test_user.id}/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # TODO(cutwater): Reduce code duplication
    #   https://issues.redhat.com/browse/AAP-5249
    role_exists = await db.scalar(
        sa.select(
            sa.exists(models.user_roles).where(
                models.user_roles.c.user_id == test_user.id,
                models.user_roles.c.role_id == role_id,
            )
        )
    )
    assert role_exists

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.USER, Action.UPDATE
    )


async def test_add_user_role_user_not_exist(
    client: AsyncClient, db: AsyncSession
):
    invalid_user_id = "42424242-4242-4242-4242-424242424242"
    role_id = await create_role(db, "test-role")
    await db.commit()

    response = await client.put(
        f"/api/users/{invalid_user_id}/roles/{role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_add_user_role_role_not_exist(
    client: AsyncClient, test_user: models.User
):
    invalid_role_id = "42424242-4242-4242-4242-424242424242"

    response = await client.put(
        f"/api/users/{test_user.id}/roles/{invalid_role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_add_user_role_duplicate(
    client: AsyncClient, db: AsyncSession, test_user: models.User
):
    role_id = await create_role(db, "test-role")
    await add_user_role(db, test_user.id, role_id)
    await db.commit()

    # Attempt to create an existing binding must return successful status code.
    response = await client.put(f"/api/users/{test_user.id}/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_remove_user_role(
    client: AsyncClient,
    db: AsyncSession,
    test_user: models.User,
    check_permission_spy: mock.Mock,
):
    role_id = await create_role(db, "test-role")
    await add_user_role(db, test_user.id, role_id)
    await db.commit()

    response = await client.delete(
        f"/api/users/{test_user.id}/roles/{role_id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.USER, Action.UPDATE
    )


async def test_remove_user_role_user_not_exist(
    client: AsyncClient, db: AsyncSession
):
    invalid_user_id = "42424242-4242-4242-4242-424242424242"
    role_id = await create_role(db, "test-role")
    await db.commit()

    response = await client.delete(
        f"/api/users/{invalid_user_id}/roles/{role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_remove_user_role_role_not_exist(
    client: AsyncClient, test_user: models.User
):
    invalid_role_id = "42424242-4242-4242-4242-424242424242"
    response = await client.delete(
        f"/api/users/{test_user.id}/roles/{invalid_role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Test list roles
async def test_list_me_roles(
    app: FastAPI,
    client: AsyncClient,
    db: AsyncSession,
    test_user: models.User,
    check_permission_spy: mock.Mock,
):
    role_ids = await _prepare_test_user_roles(db, test_user.id)
    with override_dependencies(app, {current_active_user: lambda: test_user}):
        response = await client.get("/api/users/me/roles")
    _check_test_user_roles_response(response, role_ids)
    # Only the user themselves is allowed to read their roles
    check_permission_spy.assert_not_called()


async def test_list_user_roles(
    client: AsyncClient,
    db: AsyncSession,
    test_user: models.User,
    check_permission_spy: mock.Mock,
):
    role_ids = await _prepare_test_user_roles(db, test_user.id)
    await db.commit()

    response = await client.get(f"/api/users/{test_user.id}/roles")
    _check_test_user_roles_response(response, role_ids)
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.USER, Action.READ
    )


# Test list permissions
async def test_list_me_permissions(
    app: FastAPI,
    client: AsyncClient,
    db: AsyncSession,
    test_user: models.User,
    check_permission_spy: mock.Mock,
):
    await _prepare_test_user_roles(db, test_user.id)
    with override_dependencies(app, {current_active_user: lambda: test_user}):
        response = await client.get("/api/users/me/permissions")
    _check_test_user_permissions_response(response)
    # Only the user themselves is allowed to read their roles
    check_permission_spy.assert_not_called()


async def test_list_user_permissions(
    client: AsyncClient,
    db: AsyncSession,
    test_user: models.User,
    check_permission_spy: mock.Mock,
):
    await _prepare_test_user_roles(db, test_user.id)
    await db.commit()
    response = await client.get(f"/api/users/{test_user.id}/permissions")
    _check_test_user_permissions_response(response)
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.USER, Action.READ
    )
