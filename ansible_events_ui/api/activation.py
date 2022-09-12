"""Activation API endpoints."""
import logging

import sqlalchemy as sa
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schema
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session

logger = logging.getLogger("ansible_events_ui")

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/api/activations/",
    response_model=schema.ActivationBaseRead,
    operation_id="create_activation",
)
async def create_activation(
    activation: schema.ActivationCreate,
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.insert(models.activations).values(
        name=activation.name,
        description=activation.description,
        rulebook_id=activation.rulebook_id,
        inventory_id=activation.inventory_id,
        execution_environment=activation.execution_environment,
        working_directory=activation.working_directory,
        restart_policy_id=activation.restart_policy_id,
        playbook_id=activation.playbook_id,
        activation_enabled=activation.activation_enabled,
        extra_var_id=activation.extra_var_id,
    )
    try:
        result = await db.execute(query)
    except sa.exc.IntegrityError:
        raise HTTPException(status_code=422, detail="Unprocessable Entity.")
    await db.commit()
    (id_,) = result.inserted_primary_key

    return {**activation.dict(), "id": id_}


@router.get(
    "/api/activation/{activation_id}",
    response_model=schema.ActivationRead,
    operation_id="show_activation",
)
async def read_activation(
    activation_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.activations.c.id,
            models.activations.c.name,
            models.activations.c.description,
            models.activations.c.activation_enabled,
            models.activations.c.activation_status,
            models.activations.c.working_directory,
            models.activations.c.execution_environment,
            models.activations.c.restarted_at,
            models.activations.c.restarted_count,
            models.activations.c.created_at,
            models.activations.c.modified_at,
            models.rulebooks.c.id.label("rulebook_id"),
            models.rulebooks.c.name.label("rulebook_name"),
            models.inventories.c.id.label("inventory_id"),
            models.inventories.c.name.label("inventory_name"),
            models.extra_vars.c.id.label("extra_var_id"),
            models.extra_vars.c.name.label("extra_var_name"),
            models.playbooks.c.id.label("playbook_id"),
            models.playbooks.c.name.label("playbook_name"),
            models.restart_policies.c.id.label("restart_policy_id"),
            models.restart_policies.c.name.label("restart_policy_name"),
        )
        .select_from(
            models.activations.join(models.rulebooks)
            .join(models.inventories)
            .join(models.extra_vars)
            .join(models.playbooks)
            .join(models.restart_policies)
        )
        .where(models.activations.c.id == activation_id)
    )
    result = (await db.execute(query)).one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Activation Not Found.")
    return result


@router.patch(
    "/api/activation/{activation_id}",
    response_model=schema.ActivationBaseRead,
    operation_id="update_activation",
)
async def update_activation(
    activation_id: int,
    activation: schema.ActivationUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    stored_activation = (
        await db.execute(
            sa.select(models.activations).where(
                models.activations.c.id == activation_id
            )
        )
    ).one_or_none()
    if stored_activation is None:
        raise HTTPException(status_code=404, detail="Activation Not Found.")

    await db.execute(
        sa.update(models.activations)
        .where(models.activations.c.id == activation_id)
        .values(
            name=activation.name,
            description=activation.description,
            activation_enabled=activation.activation_enabled,
        )
    )
    await db.commit()

    updated_activation = (
        await db.execute(
            sa.select(models.activations).where(
                models.activations.c.id == activation_id
            )
        )
    ).one_or_none()

    return updated_activation
