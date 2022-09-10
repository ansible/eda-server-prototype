import uuid
from typing import List

import sqlalchemy as sa
import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException, Response, status

from ansible_events_ui import schemas
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session

router = APIRouter(prefix="/api/roles", tags=["roles"])


async def role_exists_or_404(role_id: uuid.UUID, db: AsyncSession):
    role_exists = await db.scalar(
        sa.select(sa.exists().where(models.roles.c.id == role_id))
    )
    if not role_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get(
    "",
    response_model=List[schemas.RoleRead],
    operation_id="list_roles",
)
async def list_roles(db: AsyncSession = Depends(get_db_session)):
    return (await db.execute(sa.select(models.roles))).all()


@router.post(
    "",
    response_model=schemas.RoleRead,
    operation_id="create_role",
)
async def create_role(
    data: schemas.RoleCreate, db: Session = Depends(get_db_session)
):
    query = sa.insert(models.roles).values(
        name=data.name, description=data.description
    )
    try:
        (role_id,) = (await db.execute(query)).inserted_primary_key
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    await db.commit()
    return schemas.RoleRead(
        id=role_id, name=data.name, description=data.description
    )


@router.get(
    "/{role_id}",
    response_model=schemas.RoleRead,
    operation_id="show_role",
)
async def show_role(role_id: uuid.UUID, db: Session = Depends(get_db_session)):
    query = sa.select(models.roles).where(models.roles.c.id == role_id)
    role = (await db.execute(query)).one_or_none()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return role


@router.get(
    "/{role_id}/permissions",
    response_model=List[schemas.RolePermissionRead],
    operation_id="list_role_permissions",
)
async def list_role_permissions(
    role_id: uuid.UUID, db: Session = Depends(get_db_session)
):
    await role_exists_or_404(role_id, db)

    queue = sa.select(
        models.role_permissions.c.id,
        models.role_permissions.c.resource_type,
        models.role_permissions.c.action,
    ).where(models.role_permissions.c.role_id == role_id)
    return (await db.execute(queue)).all()


@router.post(
    "/{id}/permissions",
    response_model=schemas.RolePermissionRead,
    operation_id="add_role_permission",
)
async def add_role_permissions(
    id: uuid.UUID,
    data: schemas.RolePermissionCreate,
    db: Session = Depends(get_db_session),
):
    await role_exists_or_404(id, db)

    result = await db.execute(
        sa.insert(models.role_permissions).values(
            role_id=id,
            resource_type=data.resource_type,
            action=data.action,
        )
    )
    (permission_id,) = result.inserted_primary_key
    await db.commit()

    return schemas.RolePermissionRead(
        id=permission_id,
        resource_type=data.resource_type,
        action=data.action,
    )


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    operation_id="delete_role_permission",
)
async def delete_role_permission(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    db: Session = Depends(get_db_session),
):
    role_exists = await db.scalar(
        sa.select(sa.exists().where(models.roles.c.id == role_id))
    )
    if not role_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        sa.delete(models.role_permissions).where(
            models.role_permissions.c.id == permission_id
        )
    )
    await db.commit()

    if not result.rowcount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
