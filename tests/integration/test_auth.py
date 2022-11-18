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
    user = await UserDatabase(db).create(
        {
            "email": "admin@example.com",
            "hashed_password": "",
            "is_superuser": True,
        }
    )
    await db.commit()
    return user


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
    await db.commit()
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
