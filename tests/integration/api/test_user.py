import operator
import uuid
from typing import List, Tuple

import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, ResourceType
from tests.integration.utils.db import get_admin_user


async def _create_user(db: AsyncSession, email: str):
    user = models.User(email=email, hashed_password="")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# TODO(cutwater): Reduce code duplication
#   https://issues.redhat.com/browse/AAP-5249
async def _create_role(
    db: AsyncSession, name: str, description: str = ""
) -> uuid.UUID:
    (role_id,) = (
        await db.execute(
            sa.insert(models.roles).values(name=name, description=description)
        )
    ).inserted_primary_key
    await db.commit()
    return role_id


async def _create_role_permissions(
    db: AsyncSession,
    role_id: uuid.UUID,
    permissions: List[Tuple[ResourceType, Action]],
):
    query = sa.insert(models.role_permissions)
    result = await db.execute(
        query,
        [
            {"role_id": role_id, "resource_type": item[0], "action": item[1]}
            for item in permissions
        ],
    )
    await db.commit()
    return [pk[0] for pk in result.inserted_primary_key_rows]


async def _add_user_roles(
    db: AsyncSession,
    user_id: uuid.UUID,
    role_ids: List[uuid.UUID],
):
    query = sa.insert(models.user_roles)
    await db.execute(
        query,
        [{"user_id": user_id, "role_id": role_id} for role_id in role_ids],
    )
    await db.commit()


async def _prepare_test_user_roles(db: AsyncSession, user_id: uuid.UUID):
    role_ids = [
        await _create_role(db, "test-role__0"),
        await _create_role(db, "test-role__1"),
    ]
    await _create_role_permissions(
        db,
        role_ids[0],
        [
            (ResourceType.PROJECT, Action.CREATE),
            (ResourceType.PROJECT, Action.READ),
            (ResourceType.PROJECT, Action.UPDATE),
            (ResourceType.PROJECT, Action.DELETE),
        ],
    )
    await _create_role_permissions(
        db,
        role_ids[1],
        [
            (ResourceType.PROJECT, Action.READ),
            (ResourceType.PLAYBOOK, Action.READ),
            (ResourceType.EXECUTION_ENV, Action.READ),
            (ResourceType.INVENTORY, Action.READ),
        ],
    )
    await _add_user_roles(db, user_id, role_ids)
    return role_ids


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


async def test_add_user_role(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_id = await _create_role(db, "test-role")

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


async def test_add_user_role_user_not_exist(
    client: AsyncClient, db: AsyncSession
):
    invalid_user_id = "42424242-4242-4242-4242-424242424242"
    role_id = await _create_role(db, "test-role")

    response = await client.put(
        f"/api/users/{invalid_user_id}/roles/{role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_add_user_role_role_not_exist(
    client: AsyncClient, db: AsyncSession
):
    user = await _create_user(db, "test-user@example.com")
    invalid_role_id = "42424242-4242-4242-4242-424242424242"

    response = await client.put(
        f"/api/users/{user.id}/roles/{invalid_role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_add_user_role_duplicate(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_id = await _create_role(db, "test-role")
    await _add_user_roles(db, user.id, [role_id])

    # Attempt to create an existing binding must return successful status code.
    response = await client.put(f"/api/users/{user.id}/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_remove_user_role(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_id = await _create_role(db, "test-role")
    await _add_user_roles(db, user.id, [role_id])

    response = await client.delete(f"/api/users/{user.id}/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_remove_user_role_user_not_exist(
    client: AsyncClient, db: AsyncSession
):
    invalid_user_id = "42424242-4242-4242-4242-424242424242"
    role_id = await _create_role(db, "test-role")

    response = await client.delete(
        f"/api/users/{invalid_user_id}/roles/{role_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


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


async def test_list_me_roles(client: AsyncClient, db: AsyncSession):
    user = await get_admin_user(db)
    role_ids = await _prepare_test_user_roles(db, user.id)
    response = await client.get("/api/users/me/roles")
    _check_test_user_roles_response(response, role_ids)


async def test_list_user_roles(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    role_ids = await _prepare_test_user_roles(db, user.id)
    response = await client.get(f"/api/users/{user.id}/roles")
    _check_test_user_roles_response(response, role_ids)


# Test list permissions


async def test_list_me_permissions(client: AsyncClient, db: AsyncSession):
    user = await get_admin_user(db)
    await _prepare_test_user_roles(db, user.id)
    response = await client.get("/api/users/me/permissions")
    _check_test_user_permissions_response(response)


async def test_list_user_permissions(client: AsyncClient, db: AsyncSession):
    user = await _create_user(db, "test-user@example.com")
    await _prepare_test_user_roles(db, user.id)
    response = await client.get(f"/api/users/{user.id}/permissions")
    _check_test_user_permissions_response(response)
