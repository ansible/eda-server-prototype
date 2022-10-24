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

"""Job API endpoints."""

import asyncio
import logging
import uuid
from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.auth import requires_permission
from eda_server.db import models
from eda_server.db.dependency import get_db_session, get_db_session_factory
from eda_server.managers import taskmanager
from eda_server.ruleset import run_job, write_job_events
from eda_server.types import Action, ResourceType

logger = logging.getLogger("eda_server")

__all__ = ("router",)

router = APIRouter(tags=["jobs"])


@router.get(
    "/api/job_instances",
    response_model=List[schema.JobInstanceRead],
    operation_id="list_job_instances",
    dependencies=[Depends(requires_permission(ResourceType.JOB, Action.READ))],
)
async def list_job_instances(db: AsyncSession = Depends(get_db_session)):
    query = (
        sa.select(
            models.job_instances,
            models.audit_rules.c.fired_date,
            models.audit_rules.c.status,
        )
        .select_from(models.job_instances)
        .outerjoin(
            models.audit_rules,
            models.audit_rules.c.job_instance_id == models.job_instances.c.id,
        )
    )
    result = await db.execute(query)
    return result.all()


@router.post(
    "/api/job_instance",
    response_model=schema.JobInstanceBaseRead,
    operation_id="create_job_instance",
    dependencies=[
        Depends(requires_permission(ResourceType.JOB, Action.CREATE))
    ],
)
async def create_job_instance(
    j: schema.JobInstanceCreate,
    db: AsyncSession = Depends(get_db_session),
    db_factory=Depends(get_db_session_factory),
):

    query = sa.select(models.playbooks).where(
        models.playbooks.c.id == j.playbook_id
    )
    playbook_row = (await db.execute(query)).first()

    query = sa.select(models.inventories).where(
        models.inventories.c.id == j.inventory_id
    )
    inventory_row = (await db.execute(query)).first()

    query = sa.select(models.extra_vars).where(
        models.extra_vars.c.id == j.extra_var_id
    )
    extra_var_row = (await db.execute(query)).first()

    job_uuid = str(uuid.uuid4())

    query = sa.insert(models.job_instances).values(
        uuid=job_uuid,
        name=playbook_row.name,
    )
    result = await db.execute(query)
    await db.commit()
    (job_instance_id,) = result.inserted_primary_key

    event_log = asyncio.Queue()

    task = asyncio.create_task(
        run_job(
            job_uuid,
            event_log,
            playbook_row.playbook,
            inventory_row.inventory,
            extra_var_row.extra_var,
            db,
        ),
        name=f"run_job {job_instance_id}",
    )
    taskmanager.tasks.append(task)
    task = asyncio.create_task(
        write_job_events(event_log, job_instance_id, db_factory),
        name=f"write_job_events {job_instance_id}",
    )
    taskmanager.tasks.append(task)
    return {**j.dict(), "id": job_instance_id, "uuid": job_uuid}


@router.post(
    "/api/job_instance/{job_instance_id}",
    response_model=schema.JobInstanceRead,
    operation_id="rerun_job_instance",
)
async def rerun_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.job_instances).where(
        models.job_instances.c.id == job_instance_id
    )
    job_instance = (await db.execute(query)).first()
    if not job_instance:
        error = f"Job instance {job_instance_id} not found"
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error
        )

    logger.info("job_instance: %s", job_instance)

    query = (
        sa.select(models.activation_instances)
        .select_from(models.activation_instances)
        .join(
            models.activation_instance_job_instances,
            models.activation_instance_job_instances.c.job_instance_id
            == job_instance.id,
        )
        .where(
            models.activation_instance_job_instances.c.activation_instance_id
            == models.activation_instances.c.id
        )
    )
    activation_instance = (await db.execute(query)).first()

    if not activation_instance:
        error = f"Activation instance related with {job_instance_id} not found"
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error
        )

    logger.info("activation_instance: %s", activation_instance)

    query = sa.select(models.playbooks).where(
        models.playbooks.c.name == job_instance.name,
        models.playbooks.c.project_id == activation_instance.project_id,
    )
    playbook_row = (await db.execute(query)).first()

    if not playbook_row:
        error = f"Playbook {job_instance.name} not found"
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error
        )

    logger.info("playbook_row: %s", playbook_row)

    query = sa.select(models.extra_vars).where(
        models.extra_vars.c.id == activation_instance.extra_var_id,
    )
    extra_var_row = (await db.execute(query)).first()

    if not extra_var_row:
        error = f"extra_var {activation_instance.extra_var_id} not found"
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error
        )
    logger.info("extra_var_row: %s", extra_var_row)

    query = sa.select(models.inventories).where(
        models.inventories.c.id == activation_instance.inventory_id,
    )
    inventory_row = (await db.execute(query)).first()
    if not inventory_row:
        error = f"inventory {activation_instance.inventory_id} not found"
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error
        )
    logger.info("inventory_row: %s", inventory_row)

    logger.debug(
        "Job rerun using playbook: %s, extra_vars: %s",
        playbook_row.playbook,
        extra_var_row.extra_var,
    )

    job_uuid = str(uuid.uuid4())

    query = sa.insert(models.job_instances).values(
        uuid=job_uuid,
        name=job_instance.name,
        ruleset=job_instance.ruleset,
        rule=job_instance.rule,
        hosts=job_instance.hosts,
        action=job_instance.action,
    )
    result = await db.execute(query)
    await db.commit()
    (new_job_instance_id,) = result.inserted_primary_key

    event_log = asyncio.Queue()

    task = asyncio.create_task(
        run_job(
            job_uuid,
            event_log,
            playbook_row.playbook,
            inventory_row.inventory,
            extra_var_row.extra_var,
            db,
        ),
        name=f"rerun_job {job_instance_id}",
    )
    taskmanager.tasks.append(task)
    task = asyncio.create_task(
        write_job_events(event_log, new_job_instance_id, db),
        name=f"write_job_events {new_job_instance_id}",
    )
    taskmanager.tasks.append(task)

    query = sa.insert(models.activation_instance_job_instances).values(
        job_instance_id=new_job_instance_id,
        activation_instance_id=activation_instance.activation_instance_id,
    )
    await db.execute(query)
    await db.commit()

    return {
        "playbook_id": playbook_row.id,
        "inventory_id": inventory_row.id,
        "extra_var_id": extra_var_row.id,
        "id": new_job_instance_id,
        "uuid": job_uuid,
    }


@router.get(
    "/api/job_instance/{job_instance_id}",
    response_model=schema.JobInstanceRead,
    operation_id="read_job_instance",
    dependencies=[Depends(requires_permission(ResourceType.JOB, Action.READ))],
)
async def read_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.job_instances,
            models.audit_rules.c.fired_date,
            models.audit_rules.c.status,
        )
        .select_from(models.job_instances)
        .outerjoin(
            models.audit_rules,
            models.audit_rules.c.job_instance_id == models.job_instances.c.id,
        )
    ).where(models.job_instances.c.id == job_instance_id)
    result = await db.execute(query)
    return result.first()


@router.delete(
    "/api/job_instance/{job_instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_job_instance",
    dependencies=[
        Depends(requires_permission(ResourceType.JOB, Action.DELETE))
    ],
)
async def delete_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.delete(models.job_instances).where(
        models.job_instances.c.id == job_instance_id
    )
    results = await db.execute(query)
    if results.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/api/job_instance_events/{job_instance_id}",
    operation_id="read_job_instance_events",
    dependencies=[Depends(requires_permission(ResourceType.JOB, Action.READ))],
)
async def read_job_instance_events(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.job_instances).where(
        models.job_instances.c.id == job_instance_id
    )
    job = (await db.execute(query)).first()

    query = (
        sa.select(models.job_instance_events)
        .where(models.job_instance_events.c.job_uuid == job.uuid)
        .order_by(models.job_instance_events.c.counter)
    )
    return (await db.execute(query)).all()
