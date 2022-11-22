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

"""Activation API endpoints."""

import json
import logging
from typing import List

import aiodocker.exceptions
import sqlalchemy as sa
from asyncpg_lostream.lostream import PGLargeObject
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.auth import requires_permission
from eda_server.config import Settings, get_settings
from eda_server.db import models
from eda_server.db.dependency import get_db_session, get_db_session_factory
from eda_server.managers import updatemanager
from eda_server.messages import ActivationErrorMessage
from eda_server.ruleset import activate_rulesets, inactivate_rulesets
from eda_server.types import Action, ResourceType

logger = logging.getLogger("eda_server")

__all__ = ("router",)

router = APIRouter(tags=["activations"])


async def dependent_object_exists_or_exception(db: AsyncSession, activation):
    activation_dependent_objects = [
        (models.rulebooks, "rulebook", activation.rulebook_id),
        (models.inventories, "inventory", activation.inventory_id),
        (models.extra_vars, "extra_var", activation.extra_var_id),
        (models.projects, "project", activation.project_id),
    ]

    for object_model, object_name, object_id in activation_dependent_objects:
        object_exists = await db.scalar(
            sa.select(sa.exists().where(object_model.c.id == object_id))
        )
        if not object_exists:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"{object_name.capitalize()} with ID={object_id} does"
                    " not exist."
                ),
            )


@router.post(
    "/api/activations",
    response_model=schema.ActivationBaseRead,
    operation_id="create_activation",
    dependencies=[
        Depends(requires_permission(ResourceType.ACTIVATION, Action.CREATE)),
    ],
    status_code=status.HTTP_201_CREATED,
)
async def create_activation(
    activation: schema.ActivationCreate,
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.insert(models.activations).values(
        name=activation.name,
        description=activation.description,
        status=activation.status,
        rulebook_id=activation.rulebook_id,
        inventory_id=activation.inventory_id,
        execution_environment=activation.execution_environment,
        working_directory=activation.working_directory,
        restart_policy=activation.restart_policy,
        is_enabled=activation.is_enabled,
        extra_var_id=activation.extra_var_id,
    )
    try:
        result = await db.execute(query)
    except sa.exc.IntegrityError:
        await db.rollback()
        await dependent_object_exists_or_exception(db, activation)

    await db.commit()
    (id_,) = result.inserted_primary_key

    return {**activation.dict(), "id": id_}


@router.get(
    "/api/activations/{activation_id}",
    response_model=schema.ActivationRead,
    operation_id="read_activation",
    dependencies=[
        Depends(requires_permission(ResourceType.ACTIVATION, Action.READ)),
    ],
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
            models.activations.c.restart_policy,
            models.activations.c.restarted_at,
            models.activations.c.restart_count,
            models.activations.c.created_at,
            models.activations.c.modified_at,
            sa.func.jsonb_build_object(
                "id",
                models.rulebooks.c.id,
                "name",
                models.rulebooks.c.name,
            ).label("rulebook"),
            sa.func.jsonb_build_object(
                "id",
                models.inventories.c.id,
                "name",
                models.inventories.c.name,
            ).label("inventory"),
            sa.case(
                (models.extra_vars.c.id.is_(None), None),
                else_=sa.func.jsonb_build_object(
                    "id",
                    models.extra_vars.c.id,
                    "name",
                    models.extra_vars.c.name,
                ),
            ).label("extra_var"),
        )
        .select_from(models.activations)
        .join(models.rulebooks)
        .join(models.inventories)
        .outerjoin(models.extra_vars)
        .where(models.activations.c.id == activation_id)
    )

    activation = (await db.execute(query)).one_or_none()
    if activation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activation Not Found.",
        )

    return activation


@router.get(
    "/api/activations",
    response_model=List[schema.ActivationRead],
    operation_id="list_activations",
    dependencies=[
        Depends(requires_permission(ResourceType.ACTIVATION, Action.READ)),
    ],
)
async def list_activations(
    db: AsyncSession = Depends(get_db_session),
):
    activations = await db.execute(sa.select(models.activations.c.id))

    extended_activations = []
    for activation in activations:
        extended_activations.append(
            await read_activation(activation["id"], db)
        )

    return extended_activations


@router.patch(
    "/api/activations/{activation_id}",
    response_model=schema.ActivationBaseRead,
    operation_id="update_activation",
    dependencies=[
        Depends(requires_permission(ResourceType.ACTIVATION, Action.UPDATE)),
    ],
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activation Not Found.",
        )

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


@router.delete(
    "/api/activations/{activation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_activation",
    dependencies=[
        Depends(requires_permission(ResourceType.ACTIVATION, Action.DELETE)),
    ],
)
async def delete_activation(
    activation_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.delete(models.activations).where(
        models.activations.c.id == activation_id
    )
    results = await db.execute(query)
    if results.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activation Not Found.",
        )
    await db.commit()


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


@router.post(
    "/api/activation_instance",
    response_model=schema.ActivationInstanceBaseRead,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ActivationErrorMessage
        }
    },
    operation_id="create_activation_instance",
    dependencies=[
        Depends(
            requires_permission(
                ResourceType.ACTIVATION_INSTANCE, Action.CREATE
            )
        ),
    ],
)
async def create_activation_instance(
    a: schema.ActivationInstanceCreate,
    db: AsyncSession = Depends(get_db_session),
    db_factory=Depends(get_db_session_factory),
    settings: Settings = Depends(get_settings),
):
    query = (
        sa.insert(models.activation_instances)
        .values(
            name=a.name,
            rulebook_id=a.rulebook_id,
            inventory_id=a.inventory_id,
            extra_var_id=a.extra_var_id,
            working_directory=a.working_directory,
            execution_environment=a.execution_environment,
            project_id=a.project_id,
        )
        .returning(
            models.activation_instances.c.id,
            models.activation_instances.c.large_data_id,
        )
    )
    try:
        result = await db.execute(query)
    except sa.exc.IntegrityError:
        await db.rollback()
        await dependent_object_exists_or_exception(db, a)
    await db.commit()
    id_, large_data_id = result.first()

    query = (
        sa.select(
            models.inventories.c.inventory,
            models.rulebooks.c.rulesets,
            models.extra_vars.c.extra_var,
        )
        .join(
            models.inventories,
            models.activation_instances.c.inventory_id
            == models.inventories.c.id,
        )
        .join(
            models.rulebooks,
            models.activation_instances.c.rulebook_id == models.rulebooks.c.id,
        )
        .join(
            models.extra_vars,
            models.activation_instances.c.extra_var_id
            == models.extra_vars.c.id,
        )
        .where(models.activation_instances.c.id == id_)
    )
    activation_data = (await db.execute(query)).first()

    try:
        await activate_rulesets(
            settings.deployment_type,
            id_,
            large_data_id,
            a.execution_environment,
            activation_data.rulesets,
            activation_data.inventory,
            activation_data.extra_var,
            a.working_directory,
            settings.server_name,
            settings.port,
            db_factory,
        )
    except aiodocker.exceptions.DockerError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Error occurred while activating rulesets.",
                "detail": str(e),
            },
        )

    return {**a.dict(), "id": id_}


# FIXME(cutwater): The URL is not related to activation instances.
# TODO(cutwater): Maybe should be "activation_instance:deactivate"
@router.post(
    "/api/deactivate",
    operation_id="deactivate_activation_instance",
    dependencies=[
        Depends(
            requires_permission(
                ResourceType.ACTIVATION_INSTANCE, Action.UPDATE
            )
        ),
    ],
)
async def deactivate(activation_instance_id: int):
    await inactivate_rulesets(activation_instance_id)


@router.get(
    "/api/activation_instances",
    response_model=List[schema.ActivationInstanceBaseRead],
    operation_id="list_activation_instances",
    dependencies=[
        Depends(
            requires_permission(ResourceType.ACTIVATION_INSTANCE, Action.READ)
        ),
    ],
)
async def list_activation_instances(
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.select(models.activation_instances)
    result = await db.execute(query)
    return result.all()


@router.get(
    "/api/activation_instance/{activation_instance_id}",
    response_model=schema.ActivationInstanceRead,
    operation_id="read_activation_instance",
    dependencies=[
        Depends(
            requires_permission(ResourceType.ACTIVATION_INSTANCE, Action.READ)
        ),
    ],
)
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
            models.extra_vars.c.name.label("extra_var_name"),
        )
        .select_from(
            models.activation_instances.join(models.rulebooks)
            .join(models.inventories)
            .join(models.extra_vars)
        )
        .where(models.activation_instances.c.id == activation_instance_id)
    )
    activation_instance = (await db.execute(query)).first()

    if activation_instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activation instance Not Found.",
        )
    return activation_instance


@router.delete(
    "/api/activation_instance/{activation_instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_activation_instance",
    dependencies=[
        Depends(
            requires_permission(
                ResourceType.ACTIVATION_INSTANCE, Action.DELETE
            )
        ),
    ],
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
    "/api/activation_instance_logs",
    operation_id="list_activation_instance_logs",
    response_model=List[schema.ActivationLog],
    dependencies=[
        Depends(
            requires_permission(ResourceType.ACTIVATION_INSTANCE, Action.READ)
        ),
    ],
)
async def stream_activation_instance_logs(
    activation_instance_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    query = sa.select(models.activation_instances.c.large_data_id).where(
        models.activation_instances.c.id == activation_instance_id
    )
    activation_instance = (await db.execute(query)).first()
    if activation_instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    large_data_id = activation_instance.large_data_id

    async with PGLargeObject(db, oid=large_data_id, mode="r") as lobject:
        async for buff in lobject:
            await updatemanager.broadcast(
                f"/activation_instance/{activation_instance_id}",
                json.dumps(["Stdout", {"stdout": buff.decode()}]),
            )

    # Empty list return to satisfy the UI get() call
    return []


@router.get(
    "/api/activation_instance_job_instances/{activation_instance_id}",
    response_model=List[schema.JobInstanceRead],
    operation_id="list_activation_instance_job_instances",
    dependencies=[
        Depends(
            requires_permission(ResourceType.ACTIVATION_INSTANCE, Action.READ)
        ),
    ],
)
async def list_activation_instance_job_instances(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.job_instances.c.id,
            models.job_instances.c.uuid,
            models.job_instances.c.action,
            models.job_instances.c.name,
            models.job_instances.c.ruleset,
            models.job_instances.c.rule,
            models.job_instances.c.hosts,
            models.audit_rules.c.fired_date,
            models.audit_rules.c.status,
        )
        .select_from(models.job_instances)
        .join(models.activation_instance_job_instances)
        .outerjoin(models.audit_rules)
        .where(
            models.activation_instance_job_instances.c.activation_instance_id
            == activation_instance_id
        )
    )

    result = await db.execute(query)

    return result.all()
