import sqlalchemy as sa
from fastapi import Depends, HTTPException, status

from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.db.session import Session
from ansible_events_ui.types import Action, ResourceType
from ansible_events_ui.users import current_active_user


async def check_permission(
    db: Session,
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
        db: Session = Depends(get_db_session),
    ):
        if not await check_permission(
            db,
            user,
            resource_type,
            action,
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return requires_permission_dependency
