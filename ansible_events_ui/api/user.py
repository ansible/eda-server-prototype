import uuid

import sqlalchemy as sa
import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Response, status

from ansible_events_ui import schemas
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.db.session import Session
from ansible_events_ui.users import current_active_user, fastapi_users

router = APIRouter(prefix="/api/users", tags=["users"])
router.include_router(
    fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate)
)


async def _user_exists_or_404(db: Session, user_id: uuid.UUID) -> None:
    exists = await db.scalar(
        sa.select(sa.exists().where(models.User.id == user_id))
    )
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def _user_role_ids_query(user_id: uuid.UUID):
    query = (
        sa.select(models.roles.c.id)
        .join(models.user_roles)
        .where(models.user_roles.c.user_id == user_id)
    )
    return query


async def _get_user_roles(
    db: Session,
    user_id: uuid.UUID,
):
    subquery = _user_role_ids_query(user_id)
    query = sa.select(models.roles).where(models.roles.c.id.in_(subquery))
    result = await db.execute(query)
    return result.all()


async def _get_aggregated_user_permissions(
    db: Session,
    user_id: uuid.UUID,
):
    role_ids_query = _user_role_ids_query(user_id)
    query = (
        sa.select(
            models.role_permissions.c.resource_type,
            sa.func.array_agg(models.role_permissions.c.action).label(
                "actions"
            ),
        )
        .where(models.role_permissions.c.role_id.in_(role_ids_query))
        .group_by(models.role_permissions.c.resource_type)
    )
    rows = (await db.execute(query)).all()
    return {row["resource_type"]: row["actions"] for row in rows}


async def _add_user_role(db: Session, user_id: uuid.UUID, role_id: uuid.UUID):
    await db.execute(
        sa.insert(models.user_roles).values(user_id=user_id, role_id=role_id)
    )


async def _remove_user_role(
    db: Session, user_id: uuid.UUID, role_id: uuid.UUID
):
    await db.execute(
        sa.delete(models.user_roles).filter_by(
            user_id=user_id, role_id=role_id
        )
    )


@router.get("/me/roles")
async def list_me_roles(
    user: models.User = Depends(current_active_user),
    db: Session = Depends(get_db_session),
):
    return await _get_user_roles(db, user.id)


@router.get("/me/roles")
async def list_me_permissions(
    user: models.User = Depends(current_active_user),
    db: Session = Depends(get_db_session),
):
    return await _get_aggregated_user_permissions(db, user.id)


@router.get("/{user_id}/roles")
async def list_user_roles(
    user_id: uuid.UUID,
    db: Session = Depends(get_db_session),
):
    await _user_exists_or_404(db, user_id)
    return await _get_user_roles(db, user_id)


@router.put("/{user_id}/roles/{role_id}")
async def add_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
):
    await _user_exists_or_404(db, user_id)
    try:
        await _add_user_role(db, user_id, role_id)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{user_id}/roles/{role_id}")
async def remove_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: Session = Depends(get_db_session),
):
    await _user_exists_or_404(db, user_id)
    try:
        await _remove_user_role(db, user_id, role_id)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{user_id}/permissions")
async def list_user_permissions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db_session),
):
    await _user_exists_or_404(db, user_id)
    return await _get_aggregated_user_permissions(db, user_id)
