import operator
import uuid
from typing import List, Tuple

import pytest
import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, ResourceType


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


async def test_create_role(client: AsyncClient, db: AsyncSession):
    response = await client.post(
        "/api/roles",
        json={"name": "test-role-01", "description": "A test role 01."},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["name"] == "test-role-01"
    assert data["description"] == "A test role 01."

    role = (
        await db.execute(
            sa.select(models.roles).where(models.roles.c.id == data["id"])
        )
    ).first()

    assert role["name"] == "test-role-01"
    assert role["description"] == "A test role 01."


async def test_show_role(client: AsyncClient, db: AsyncSession):
    role_id = await _create_role(db, "test-role-02")

    response = await client.get(f"/api/roles/{role_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(role_id),
        "name": "test-role-02",
        "description": "",
    }


async def test_role_invalid_id(client: AsyncClient):
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


async def test_delete_role(client: AsyncClient, db: AsyncSession):
    role_id = await _create_role(db, "test-role-03")

    response = await client.delete(f"/api/roles/{role_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    role_exists = await db.scalar(
        sa.select(sa.exists().where(models.roles.c.id == role_id))
    )
    assert not role_exists

    # Check that subsequent DELETE request returns 404
    response = await client.delete(f"/api/roles/{role_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_role_not_exist(client: AsyncClient):
    response = await client.delete(
        "/api/roles/42424242-4242-4242-4242-424242424242"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_list_role_permissions(client: AsyncClient, db: AsyncSession):
    role_id = await _create_role(db, "test-role-04")
    await _create_role_permissions(
        db,
        role_id,
        [
            (ResourceType.PROJECT, Action.READ),
            (ResourceType.PLAYBOOK, Action.READ),
            (ResourceType.EXECUTION_ENV, Action.READ),
        ],
    )

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


async def test_add_role_permissions(client: AsyncClient, db: AsyncSession):
    role_id = await _create_role(db, "test-role-05")

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
    role_id = await _create_role(db, "test-role-06")
    response = await client.post(
        f"/api/roles/{role_id}/permissions", json=data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_delete_role_permissions(client: AsyncClient, db: AsyncSession):
    role_id = await _create_role(db, "test-role-07")
    permission_ids = await _create_role_permissions(
        db,
        role_id,
        [(ResourceType.PROJECT, Action.READ)],
    )

    response = await client.delete(
        f"/api/roles/{role_id}/permissions/{permission_ids[0]}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check that subsequent DELETE request returns 404
    response = await client.delete(
        f"/api/roles/{role_id}/permissions/{permission_ids[0]}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
