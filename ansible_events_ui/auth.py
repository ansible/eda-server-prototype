import uuid

import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.types import Action, ResourceType
from ansible_events_ui.users import current_active_user


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
