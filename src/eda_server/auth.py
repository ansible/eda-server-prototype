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
from typing import List, Tuple

import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.dependency import get_db_session
from eda_server.types import Action, ResourceType
from eda_server.users import current_active_user


async def check_permission(
    db: AsyncSession,
    user: models.User,
    resource_type: ResourceType,
    action: Action,
) -> bool:
    if user.is_superuser:
        return True

    # TODO(cutwater): Optimize queries
    query = (
        sa.select(models.roles.c.id)
        .join(models.user_roles)
        .where(models.user_roles.c.user_id == user.id)
    )
    user_role_ids = (await db.scalars(query)).all()
    query = sa.select(
        sa.exists().where(
            models.role_permissions.c.role_id.in_(user_role_ids),
            models.role_permissions.c.resource_type == resource_type,
            models.role_permissions.c.action == action,
        )
    )
    return await db.scalar(query)


def requires_permission(resource_type: ResourceType, action: Action):
    async def requires_permission_dependency(
        user: models.User = Depends(current_active_user),
        db: AsyncSession = Depends(get_db_session),
    ):
        if not await check_permission(
            db,
            user,
            resource_type,
            action,
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return requires_permission_dependency


# TODO(cutwater): The functions below will be moved under
#   the `eda_server.db.repositories` package as a part of
#   the https://issues.redhat.com/browse/AAP-5249 issue.
async def create_role(
    db: AsyncSession, name: str, description: str = ""
) -> uuid.UUID:
    (role_id,) = (
        await db.execute(
            sa.insert(models.roles).values(name=name, description=description)
        )
    ).inserted_primary_key
    return role_id


async def add_role_permissions(
    db: AsyncSession,
    role_id: uuid.UUID,
    permissions: List[Tuple[ResourceType, Action]],
) -> List[uuid.UUID]:
    query = sa.insert(models.role_permissions)
    result = await db.execute(
        query,
        [
            {"role_id": role_id, "resource_type": item[0], "action": item[1]}
            for item in permissions
        ],
    )
    return [pk[0] for pk in result.inserted_primary_key_rows]


async def get_user_roles(
    db: AsyncSession,
    user_id: uuid.UUID,
):
    subquery = _user_role_ids_query(user_id)
    query = sa.select(models.roles).where(models.roles.c.id.in_(subquery))
    result = await db.execute(query)
    return result.all()


async def get_user_permissions(
    db: AsyncSession,
    user_id: uuid.UUID,
):
    role_ids_query = _user_role_ids_query(user_id)
    permissions_query = (
        sa.select(
            models.role_permissions.c.resource_type,
            models.role_permissions.c.action,
        )
        .where(models.role_permissions.c.role_id.in_(role_ids_query))
        .distinct()
    )
    return (await db.execute(permissions_query)).all()


async def add_user_role(
    db: AsyncSession, user_id: uuid.UUID, role_id: uuid.UUID
):
    await db.execute(
        sa.insert(models.user_roles).values(user_id=user_id, role_id=role_id)
    )


async def remove_user_role(
    db: AsyncSession, user_id: uuid.UUID, role_id: uuid.UUID
):
    await db.execute(
        sa.delete(models.user_roles).filter_by(
            user_id=user_id, role_id=role_id
        )
    )


def _user_role_ids_query(user_id: uuid.UUID):
    query = (
        sa.select(models.roles.c.id)
        .join(models.user_roles)
        .where(models.user_roles.c.user_id == user_id)
    )
    return query
