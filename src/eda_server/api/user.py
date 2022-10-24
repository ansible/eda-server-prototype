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

import uuid
from typing import List

import sqlalchemy as sa
import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import auth, schema
from eda_server.auth import requires_permission
from eda_server.db import models
from eda_server.db.dependency import get_db_session
from eda_server.types import Action, ResourceType
from eda_server.users import current_active_user, fastapi_users

router = APIRouter(prefix="/api/users", tags=["users"])
router.include_router(
    fastapi_users.get_users_router(schema.UserRead, schema.UserUpdate)
)


async def _user_exists_or_404(db: AsyncSession, user_id: uuid.UUID) -> None:
    exists = await db.scalar(
        sa.select(sa.exists().where(models.User.id == user_id))
    )
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def _role_exists_or_404(db: AsyncSession, role_id: uuid.UUID):
    exists = await db.scalar(
        sa.select(sa.exists().where(models.roles.c.id == role_id))
    )
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# TODO(cutwater): Reduce code duplication
#   https://issues.redhat.com/browse/AAP-5249
async def _user_role_exists(
    db: AsyncSession, user_id: uuid.UUID, role_id: uuid.UUID
) -> None:
    return await db.scalar(
        sa.select(
            sa.exists().where(
                models.user_roles.c.user_id == user_id,
                models.user_roles.c.role_id == role_id,
            )
        )
    )


@router.get(
    "/me/roles",
    operation_id="list_my_roles",
    response_model=List[schema.RoleRead],
)
async def list_me_roles(
    user: models.User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    return await auth.get_user_roles(db, user.id)


# TODO(cutwater): Add permission checks
@router.get(
    "/{user_id}/roles",
    operation_id="list_user_roles",
    response_model=List[schema.RoleRead],
    dependencies=[
        Depends(requires_permission(ResourceType.USER, Action.READ))
    ],
)
async def list_user_roles(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    await _user_exists_or_404(db, user_id)
    return await auth.get_user_roles(db, user_id)


# TODO(cutwater): Add permission checks
@router.put(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="add_user_role",
    dependencies=[
        Depends(requires_permission(ResourceType.USER, Action.UPDATE))
    ],
)
async def add_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    if await _user_role_exists(db, user_id, role_id):
        return
    await _user_exists_or_404(db, user_id)
    await _role_exists_or_404(db, role_id)
    try:
        await auth.add_user_role(db, user_id, role_id)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    await db.commit()


# TODO(cutwater): Add permission checks
@router.delete(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="remove_user_role",
    dependencies=[
        Depends(requires_permission(ResourceType.USER, Action.UPDATE))
    ],
)
async def remove_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    await _user_exists_or_404(db, user_id)
    if not await _user_role_exists(db, user_id, role_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await auth.remove_user_role(db, user_id, role_id)
    await db.commit()


@router.get(
    "/me/permissions",
    operation_id="list_my_permissions",
    response_model=List[str],
)
async def list_me_permissions(
    user: models.User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    permissions = await auth.get_user_permissions(db, user.id)
    return ["{resource_type}:{action}".format(**p) for p in permissions]


# TODO(cutwater): Add permission checks
@router.get(
    "/{user_id}/permissions",
    operation_id="list_user_permissions",
    response_model=List[str],
    dependencies=[
        Depends(requires_permission(ResourceType.USER, Action.READ))
    ],
)
async def list_user_permissions(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    await _user_exists_or_404(db, user_id)
    permissions = await auth.get_user_permissions(db, user_id)
    return ["{resource_type}:{action}".format(**p) for p in permissions]
