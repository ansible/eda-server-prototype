"""Activation API endpoints."""
import logging

import sqlalchemy as sa
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models
from ansible_events_ui.schema.activation import Activation

from ansible_events_ui.db.dependency import get_db_session

logger = logging.getLogger("ansible_events_ui")

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/api/activations/",
    response_model=Activation,
    operation_id="create_activation",
)
async def create_activation(
    activation: Activation,
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.insert(models.activations).values(
        name=activation.name,
        description=activation.description,
        rulebook_id=activation.rulebook_id,
        inventory_id=activation.inventory_id,
        execution_env_id=activation.execution_env_id,
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
