"""Activation API endpoints."""
import json
import logging
from typing import List

import aiodocker.exceptions
import sqlalchemy as sa
import sqlalchemy.orm
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schemas
from ansible_events_ui.config import Settings, get_settings
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import (
    get_db_session,
    get_db_session_factory,
)
from ansible_events_ui.managers import updatemanager
from ansible_events_ui.ruleset import activate_rulesets, inactivate_rulesets

logger = logging.getLogger("ansible_events_ui")

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/api/activations/",
    response_model=schemas.ActivationBaseRead,
    operation_id="create_activation",
)
async def create_activation(
    activation: schemas.ActivationCreate,
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
        is_enabled=activation.is_enabled,
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
    response_model=schemas.ActivationRead,
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
            models.activations.c.is_enabled,
            models.activations.c.status,
            models.activations.c.working_directory,
            models.activations.c.execution_environment,
            models.activations.c.restarted_at,
            models.activations.c.restart_count,
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
        .select_from(models.activations)
        .join(models.rulebooks)
        .join(models.inventories)
        .join(models.extra_vars)
        .join(models.playbooks)
        .join(models.restart_policies)
        .where(models.activations.c.id == activation_id)
    )
    activation = (await db.execute(query)).one_or_none()
    if activation is None:
        raise HTTPException(status_code=404, detail="Activation Not Found.")

    response = {
        "id": activation["id"],
        "name": activation["name"],
        "description": activation["description"],
        "is_enabled": activation["is_enabled"],
        "status": activation["status"],
        "working_directory": activation["working_directory"],
        "execution_environment": activation["execution_environment"],
        "restarted_at": activation["restarted_at"],
        "restart_count": activation["restart_count"],
        "created_at": activation["created_at"],
        "modified_at": activation["modified_at"],
        "rulebook": {
            "id": activation["rulebook_id"],
            "name": activation["rulebook_name"],
        },
        "inventory": {
            "id": activation["inventory_id"],
            "name": activation["inventory_name"],
        },
        "playbook": {
            "id": activation["playbook_id"],
            "name": activation["playbook_name"],
        },
        "restart_policy": {
            "id": activation["restart_policy_id"],
            "name": activation["restart_policy_name"],
        },
        "extra_var": {
            "id": activation["extra_var_id"],
            "name": activation["extra_var_name"],
        },
    }
    return response


@router.patch(
    "/api/activation/{activation_id}",
    response_model=schemas.ActivationBaseRead,
    operation_id="update_activation",
)
async def update_activation(
    activation_id: int,
    activation: schemas.ActivationUpdate,
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
            is_enabled=activation.is_enabled,
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


async def read_output(proc, activation_instance_id, db_session_factory):
    # TODO(cutwater): Replace with FastAPI dependency injections,
    #   that is available in BackgroundTasks
    async with db_session_factory() as db:
        line_number = 0
        done = False
        while not done:
            line = await proc.stdout.readline()
            if len(line) == 0:
                done = True
                continue
            line = line.decode()
            await updatemanager.broadcast(
                f"/activation_instance/{activation_instance_id}",
                json.dumps(["Stdout", {"stdout": line}]),
            )
            query = sa.insert(models.activation_instance_logs).values(
                line_number=line_number,
                log=line,
                activation_instance_id=activation_instance_id,
            )
            await db.execute(query)
            await db.commit()
            line_number += 1


@router.post("/api/activation_instance/")
async def create_activation_instance(
    a: schemas.ActivationInstance,
    db: AsyncSession = Depends(get_db_session),
    db_session_factory: sqlalchemy.orm.sessionmaker = Depends(
        get_db_session_factory
    ),
    settings: Settings = Depends(get_settings),
):
    query = sa.select(models.rulebooks).where(
        models.rulebooks.c.id == a.rulebook_id
    )
    rulebook_row = (await db.execute(query)).first()

    query = sa.select(models.inventories).where(
        models.inventories.c.id == a.inventory_id
    )
    inventory_row = (await db.execute(query)).first()

    query = sa.select(models.extra_vars).where(
        models.extra_vars.c.id == a.extra_var_id
    )
    extra_var_row = (await db.execute(query)).first()

    query = sa.insert(models.activation_instances).values(
        name=a.name,
        rulebook_id=a.rulebook_id,
        inventory_id=a.inventory_id,
        extra_var_id=a.extra_var_id,
        working_directory=a.working_directory,
        execution_environment=a.execution_environment,
    )
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key

    try:
        await activate_rulesets(
            settings.deployment_type,
            id_,
            a.execution_environment,
            rulebook_row.rulesets,
            inventory_row.inventory,
            extra_var_row.extra_var,
            a.working_directory,
            settings.server_name,
            settings.port,
            db,
        )
    except aiodocker.exceptions.DockerError as e:
        return HTTPException(status_code=500, detail=str(e))

    return {**a.dict(), "id": id_}


@router.post("/api/deactivate/")
async def deactivate(activation_instance_id: int):
    await inactivate_rulesets(activation_instance_id)
    return


@router.get("/api/activation_instances/")
async def list_activation_instances(
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.select(models.activation_instances)
    result = await db.execute(query)
    return result.all()


@router.get("/api/activation_instance/{activation_instance_id}")
async def read_activation_instance(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.activation_instances.c.id,
            models.activation_instances.c.name,
            models.rulebooks.c.id.label("ruleset_id"),
            models.rulebooks.c.name.label("ruleset_name"),
            models.inventories.c.id.label("inventory_id"),
            models.inventories.c.name.label("inventory_name"),
            models.extra_vars.c.id.label("extra_var_id"),
            models.extra_vars.c.name.label("extra_vars_name"),
        )
        .select_from(
            models.activation_instances.join(models.rulebooks)
            .join(models.inventories)
            .join(models.extra_vars)
        )
        .where(models.activation_instances.c.id == activation_instance_id)
    )
    result = await db.execute(query)
    return result.first()


@router.delete(
    "/api/activation_instance/{activation_instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_activation_instance",
)
async def delete_activation_instance(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.delete(models.activation_instances).where(
        models.activation_instances.c.id == activation_instance_id
    )
    results = await db.execute(query)
    if results.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/api/activation_instance_logs/",
    response_model=List[schemas.ActivationLog],
)
async def list_activation_instance_logs(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(models.activation_instance_logs)
        .where(
            models.activation_instance_logs.c.activation_instance_id
            == activation_instance_id
        )
        .order_by(models.activation_instance_logs.c.id)
    )
    result = await db.execute(query)
    return result.all()


@router.get("/api/activation_instance_job_instances/{activation_instance_id}")
async def read_activation_instance_job_instances(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.activation_instance_job_instances).where(
        models.activation_instance_job_instances.c.activation_instance_id
        == activation_instance_id
    )
    result = await db.execute(query)
    return result.all()
