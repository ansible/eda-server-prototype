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

from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.auth import requires_permission
from eda_server.db import models
from eda_server.db.dependency import get_db_session
from eda_server.types import Action, InventorySource, ResourceType

router = APIRouter(tags=["inventories"])


@router.post(
    "/api/inventory",
    response_model=schema.InventoryRead,
    operation_id="create_inventory",
    dependencies=[
        Depends(requires_permission(ResourceType.INVENTORY, Action.CREATE))
    ],
)
async def create_inventory(
    inventory_: schema.InventoryCreate,
    db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(
        sa.insert(models.inventories).values(
            name=inventory_.name,
            description=inventory_.description,
            inventory=inventory_.inventory,
            inventory_source=InventorySource.USER_DEFINED,
        )
    )
    await db.commit()
    (inventory_id,) = result.inserted_primary_key

    stored_inventory = (
        await db.execute(
            sa.select(models.inventories).where(
                models.inventories.c.id == inventory_id
            )
        )
    ).one_or_none()

    return stored_inventory


@router.patch(
    "/api/inventory/{inventory_id}",
    response_model=schema.InventoryRead,
    operation_id="update_inventory",
    dependencies=[
        Depends(requires_permission(ResourceType.INVENTORY, Action.UPDATE))
    ],
)
async def update_inventory(
    inventory_id: int,
    inventory_: schema.InventoryUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    stored_inventory = (
        await db.execute(
            sa.select(models.inventories).where(
                models.inventories.c.id == inventory_id
            )
        )
    ).one_or_none()
    if stored_inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory Not Found.",
        )

    await db.execute(
        sa.update(models.inventories)
        .where(models.inventories.c.id == inventory_id)
        .values(
            name=inventory_.name,
            description=inventory_.description,
            inventory=inventory_.inventory,
        )
    )
    await db.commit()

    updated_inventory = (
        await db.execute(
            sa.select(models.inventories).where(
                models.inventories.c.id == inventory_id
            )
        )
    ).one_or_none()

    return updated_inventory


@router.get(
    "/api/inventory/{inventory_id}",
    response_model=schema.InventoryRead,
    operation_id="read_inventory",
    dependencies=[
        Depends(requires_permission(ResourceType.INVENTORY, Action.READ))
    ],
)
async def read_inventory(
    inventory_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    inventory = (
        await db.execute(
            sa.select(models.inventories).where(
                models.inventories.c.id == inventory_id
            )
        )
    ).one_or_none()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory Not Found.",
        )

    return inventory


@router.get(
    "/api/inventories",
    response_model=List[schema.InventoryRead],
    operation_id="list_inventories",
    dependencies=[
        Depends(requires_permission(ResourceType.INVENTORY, Action.READ))
    ],
)
async def list_inventories(
    db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(sa.select(models.inventories))
    return result.all()


@router.delete(
    "/api/inventory/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_inventory",
    dependencies=[
        Depends(requires_permission(ResourceType.INVENTORY, Action.DELETE)),
    ],
)
async def delete_inventory(
    inventory_id: int, db: AsyncSession = Depends(get_db_session)
):
    results = await db.execute(
        sa.delete(models.inventories).where(
            models.inventories.c.id == inventory_id
        )
    )
    if not results.rowcount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory Not Found.",
        )
    await db.commit()
