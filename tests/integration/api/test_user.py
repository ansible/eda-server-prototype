import operator
import uuid
from typing import List, Tuple

import pytest
import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.auth import add_role_permissions, add_user_role, create_role
from eda_server.db import models
from eda_server.types import Action, ResourceType
from eda_server.users import UserDatabase
from tests.integration.utils.db import get_admin_user


async def _create_user(db: AsyncSession, email: str):
    return await UserDatabase(db).create(
        {
            "email": email,
            "hashed_password": "",
        }
    )


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


@pytest.mark.asyncio
async def test_add_user_role(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_id = await create_role(db, "test-role")

    response = await client.put(f"/api/users/{user.id}/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # TODO(cutwater): Reduce code duplication
    #   https://issues.redhat.com/browse/AAP-5249
    role_exists = await db.scalar(
        sa.select(
            sa.exists(models.user_roles).where(
                models.user_roles.c.user_id == user.id,
                models.user_roles.c.role_id == role_id,
            )
        )
    )
    assert role_exists


@pytest.mark.asyncio
async def test_add_user_role_user_not_exist(
    client: AsyncClient, db: AsyncSession
):
    invalid_user_id = "42424242-4242-4242-4242-424242424242"
    role_id = await create_role(db, "test-role")

    response = await client.put(
        f"/api/users/{invalid_user_id}/roles/{role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_add_user_role_role_not_exist(
    client: AsyncClient, db: AsyncSession
):
    user = await _create_user(db, "test-user@example.com")
    invalid_role_id = "42424242-4242-4242-4242-424242424242"

    response = await client.put(
        f"/api/users/{user.id}/roles/{invalid_role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_add_user_role_duplicate(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_id = await create_role(db, "test-role")
    await add_user_role(db, user.id, role_id)

    # Attempt to create an existing binding must return successful status code.
    response = await client.put(f"/api/users/{user.id}/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_user_role(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_id = await create_role(db, "test-role")
    await add_user_role(db, user.id, role_id)

    response = await client.delete(f"/api/users/{user.id}/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_user_role_user_not_exist(
    client: AsyncClient, db: AsyncSession
):
    invalid_user_id = "42424242-4242-4242-4242-424242424242"
    role_id = await create_role(db, "test-role")

    response = await client.delete(
        f"/api/users/{invalid_user_id}/roles/{role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_user_role_role_not_exist(
    client: AsyncClient, db: AsyncSession
):
    user = await _create_user(db, "test-user@example.com")
    invalid_role_id = "42424242-4242-4242-4242-424242424242"

    response = await client.delete(
        f"/api/users/{user.id}/roles/{invalid_role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Test list roles
@pytest.mark.asyncio
async def test_list_me_roles(client: AsyncClient, db: AsyncSession):
    user = await get_admin_user(db)
    role_ids = await _prepare_test_user_roles(db, user.id)
    response = await client.get("/api/users/me/roles")
    _check_test_user_roles_response(response, role_ids)


@pytest.mark.asyncio
async def test_list_user_roles(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_ids = await _prepare_test_user_roles(db, user.id)
    response = await client.get(f"/api/users/{user.id}/roles")
    _check_test_user_roles_response(response, role_ids)


# Test list permissions
@pytest.mark.asyncio
async def test_list_me_permissions(client: AsyncClient, db: AsyncSession):
    user = await get_admin_user(db)
    await _prepare_test_user_roles(db, user.id)
    response = await client.get("/api/users/me/permissions")
    _check_test_user_permissions_response(response)


@pytest.mark.asyncio
async def test_list_user_permissions(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    await _prepare_test_user_roles(db, user.id)
    response = await client.get(f"/api/users/{user.id}/permissions")
    _check_test_user_permissions_response(response)
