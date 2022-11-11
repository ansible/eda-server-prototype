import pytest
import pytest_asyncio
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.auth import (
    add_role_permissions,
    add_user_role,
    check_permission,
    create_role,
    requires_permission,
)
from eda_server.db import models
from eda_server.types import Action, ResourceType
from eda_server.users import UserDatabase


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    return await UserDatabase(db).create(
        {
            "email": "admin@example.com",
            "hashed_password": "",
            "is_superuser": True,
        }
    )


@pytest_asyncio.fixture
async def regular_user(db: AsyncSession):
    role_id = await create_role(db, "test-role")
    await add_role_permissions(
        db,
        role_id,
        [
            (ResourceType.ROLE, Action.READ),
            (ResourceType.ROLE, Action.UPDATE),
        ],
    )
    user = await UserDatabase(db).create(
        {
            "email": "test@example.com",
            "hashed_password": "",
        }
    )
    await add_user_role(db, user.id, role_id)
    return user


@pytest.mark.asyncio
async def test_check_permission_is_superuser(
    db: AsyncSession, admin_user: models.User
):
    assert await check_permission(
        db, admin_user, ResourceType.ROLE, Action.CREATE
    )
    assert await check_permission(
        db, admin_user, ResourceType.ROLE, Action.READ
    )
    assert await check_permission(
        db, admin_user, ResourceType.ROLE, Action.UPDATE
    )
    assert await check_permission(
        db, admin_user, ResourceType.ROLE, Action.DELETE
    )


@pytest.mark.asyncio
async def test_check_permission_regular_user(
    db: AsyncSession, regular_user: models.User
):
    assert await check_permission(
        db, regular_user, ResourceType.ROLE, Action.READ
    )
    assert await check_permission(
        db, regular_user, ResourceType.ROLE, Action.UPDATE
    )
    assert not await check_permission(
        db, regular_user, ResourceType.ROLE, Action.CREATE
    )
    assert not await check_permission(
        db, regular_user, ResourceType.ROLE, Action.DELETE
    )


@pytest.mark.asyncio
async def test_requires_permission_dependency(
    db: AsyncSession, regular_user: models.User
):
    dependency = requires_permission(ResourceType.ROLE, Action.READ)
    try:
        await dependency(regular_user, db)
    except HTTPException:
        pytest.fail("Must not raise HTTPException")


@pytest.mark.asyncio
async def test_requires_permission_dependency_forbidden(
    db: AsyncSession, regular_user: models.User
):
    dependency = requires_permission(ResourceType.ROLE, Action.CREATE)

    with pytest.raises(HTTPException) as excinfo:
        await dependency(regular_user, db)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
