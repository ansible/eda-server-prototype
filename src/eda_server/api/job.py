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
from eda_server.db import models
from eda_server.db.dependency import get_db_session
from eda_server.managers import taskmanager
from eda_server.ruleset import run_job, write_job_events

logger = logging.getLogger("eda_server")

__all__ = ("router",)

router = APIRouter(tags=["jobs"])


@router.get(
    "/api/job_instances/",
    response_model=List[schema.JobInstanceBaseRead],
    operation_id="list_job_instances",
)
async def list_job_instances(db: AsyncSession = Depends(get_db_session)):
    query = sa.select(models.job_instances)
    result = await db.execute(query)
    return result.all()


@router.post(
    "/api/job_instance/",
    response_model=schema.JobInstanceRead,
    operation_id="create_job_instance",
)
async def create_job_instance(
    j: schema.JobInstanceCreate, db: AsyncSession = Depends(get_db_session)
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

    query = sa.insert(models.job_instances).values(uuid=job_uuid)
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
        write_job_events(event_log, db, job_instance_id),
        name=f"write_job_events {job_instance_id}",
    )
    taskmanager.tasks.append(task)
    return {**j.dict(), "id": job_instance_id, "uuid": job_uuid}


@router.get(
    "/api/job_instance/{job_instance_id}",
    response_model=schema.JobInstanceBaseRead,
    operation_id="read_job_instance",
)
async def read_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = sa.select(models.job_instances).where(
        models.job_instances.c.id == job_instance_id
    )
    result = await db.execute(query)
    return result.first()


@router.delete(
    "/api/job_instance/{job_instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_job_instance",
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
    response_model=List[schema.JobInstanceEventsRead],
    operation_id="read_job_instance_events",
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
