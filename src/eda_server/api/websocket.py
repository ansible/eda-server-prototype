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

import base64
import json
import logging
from datetime import datetime
from enum import Enum

from asyncpg_lostream.lostream import PGLargeObject
from fastapi import APIRouter, Depends
from sqlalchemy import cast, insert, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocket, WebSocketDisconnect

from eda_server.db import models
from eda_server.db.dependency import get_db_session_factory
from eda_server.managers import secretsmanager, updatemanager

logger = logging.getLogger("eda_server")

router = APIRouter()


# Determine host status based on event type
# https://github.com/ansible/awx/blob/devel/awx/main/models/events.py#L164
class Event(Enum):
    FAILED = "runner_on_failed"
    OK = "runner_on_ok"
    ERROR = "runner_on_error"
    SKIPPED = "runner_on_skipped"
    UNREACHABLE = "runner_on_unreachable"
    NO_HOSTS = "runner_on_no_hosts"
    POLLING = "runner_on_async_poll"
    ASYNC_OK = "runner_on_async_ok"
    ASYNC_FAILURE = "runner_on_async_failed"
    RETRY = "runner_retry"
    NO_MATCHED = "playbook_on_no_hosts_matched"
    NO_REMAINING = "playbook_on_no_hosts_remaining"


host_status_map = {
    Event.FAILED: "failed",
    Event.OK: "ok",
    Event.ERROR: "failed",
    Event.SKIPPED: "skipped",
    Event.UNREACHABLE: "unreachable",
    Event.NO_HOSTS: "no remaining",
    Event.POLLING: "polling",
    Event.ASYNC_OK: "async ok",
    Event.ASYNC_FAILURE: "async failure",
    Event.RETRY: "retry",
    Event.NO_MATCHED: "no matched",
    Event.NO_REMAINING: "no remaining",
}


@router.websocket("/api/ws2")
async def websocket_endpoint2(
    websocket: WebSocket,
    db_session_factory: sessionmaker = Depends(get_db_session_factory),
):
    logger.debug("starting ws2")
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            logger.debug(f"ws2 received: {data}")
            # TODO(cutwater): Some data validation is needed
            data_type = data.get("type")
            async with db_session_factory() as db:
                if data_type == "Worker":
                    await handle_workers(websocket, data, db)
                elif data_type == "Job":
                    await handle_jobs(data, db)
                elif data_type == "AnsibleEvent":
                    await handle_ansible_rulebook(data, db)
                elif data_type == "Action":
                    await handle_actions(data, db)
    except WebSocketDisconnect:
        pass


@router.websocket("/api/ws-activation/{activation_instance_id}")
async def websocket_activation_endpoint(
    websocket: WebSocket, activation_instance_id
):
    page = f"/activation_instance/{activation_instance_id}"
    await updatemanager.connect(page, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(data)
    except WebSocketDisconnect:
        updatemanager.disconnect(page, websocket)


@router.websocket("/api/ws-jobs")
async def websocket_jobs_endpoint(websocket: WebSocket):
    page = "/jobs"
    await updatemanager.connect(page, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(data)
    except WebSocketDisconnect:
        updatemanager.disconnect(page, websocket)


@router.websocket("/api/ws-job/{job_instance_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_instance_id):
    page = f"/job_instance/{job_instance_id}"
    await updatemanager.connect(page, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(data)
    except WebSocketDisconnect:
        updatemanager.disconnect(page, websocket)


async def send_project_data(
    large_data_id, websocket: WebSocket, db: AsyncSession
):

    async with PGLargeObject(db, oid=large_data_id, mode="r") as lobject:
        async for buff in lobject:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "ProjectData",
                        "data": base64.b64encode(buff).decode("utf-8"),
                        "more": True,
                    }
                ),
            )

        await websocket.send_text(
            json.dumps({"type": "ProjectData", "data": None, "more": False}),
        )


async def handle_workers(websocket: WebSocket, data: dict, db: AsyncSession):
    await websocket.send_text(json.dumps({"type": "Hello"}))
    query = select(models.activation_instances).where(
        models.activation_instances.c.id == data.get("activation_id")
    )
    activation = (await db.execute(query)).first()

    query = select(models.projects).where(
        models.projects.c.id == activation.project_id
    )
    project_row = (await db.execute(query)).first()
    if project_row:
        if project_row.large_data_id:
            await send_project_data(project_row.large_data_id, websocket, db)
        else:
            logger.debug("no project large_data_id")
    else:
        logger.debug("no project row")

    query = select(models.rulebooks).where(
        models.rulebooks.c.id == activation.rulebook_id
    )
    rulebook_row = (await db.execute(query)).first()
    await websocket.send_text(
        json.dumps(
            {
                "type": "Rulebook",
                "data": base64.b64encode(
                    rulebook_row.rulesets.encode()
                ).decode(),
            }
        )
    )

    query = select(models.inventories).where(
        models.inventories.c.id == activation.inventory_id
    )
    inventory_row = (await db.execute(query)).first()
    await websocket.send_text(
        json.dumps(
            {
                "type": "Inventory",
                "data": base64.b64encode(
                    inventory_row.inventory.encode()
                ).decode(),
            }
        )
    )

    query = select(models.extra_vars).where(
        models.extra_vars.c.id == activation.extra_var_id
    )
    extra_var_row = (await db.execute(query)).first()
    await websocket.send_text(
        json.dumps(
            {
                "type": "ExtraVars",
                "data": base64.b64encode(
                    extra_var_row.extra_var.encode()
                ).decode(),
            }
        )
    )
    if secretsmanager.has_secret("ssh-private-key"):
        await websocket.send_text(
            json.dumps(
                {
                    "type": "SSHPrivateKey",
                    "data": base64.b64encode(
                        secretsmanager.get_secret("ssh-private-key").encode()
                    ).decode(),
                }
            )
        )
    else:
        await websocket.send_text(
            json.dumps({"type": "SSHPrivateKey", "data": ""})
        )


async def handle_ansible_rulebook(data: dict, db: AsyncSession):
    event_data = data.get("event", {})
    if event_data.get("stdout"):
        query = select(models.job_instances).where(
            models.job_instances.c.uuid == event_data.get("job_id")
        )
        result = await db.execute(query)
        job_instance_id = result.first().job_instance_id

        await updatemanager.broadcast(
            f"/job_instance/{job_instance_id}",
            json.dumps(["Stdout", {"stdout": event_data.get("stdout")}]),
        )

    created = event_data.get("created")
    if created:
        created = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f")

    query = insert(models.job_instance_events).values(
        job_uuid=event_data.get("job_id"),
        counter=event_data.get("counter"),
        stdout=event_data.get("stdout"),
        type=event_data.get("event"),
        created_at=created,
    )
    await db.execute(query)

    event = event_data.get("event")
    if event and event in [item.value for item in host_status_map]:
        data = event_data.get("event_data", {})

        host = data.get("play_pattern")
        playbook = data.get("playbook")
        play = data.get("play")
        task = data.get("task")
        status = host_status_map[Event(event)]

        if event == "runner_on_ok" and data.get("res", {}).get("changed"):
            status = "changed"

        query = insert(models.job_instance_hosts).values(
            job_uuid=event_data.get("job_id"),
            host=host,
            playbook=playbook,
            play=play,
            task=task,
            status=status,
        )
        await db.execute(query)

    await db.commit()


async def handle_jobs(data: dict, db: AsyncSession):
    query = insert(models.job_instances).values(
        uuid=data.get("job_id"),
        name=data.get("name"),
        action=data.get("action"),
        ruleset=data.get("ruleset"),
        hosts=data.get("hosts"),
        rule=data.get("rule"),
    )
    result = await db.execute(query)
    await db.commit()
    (job_instance_id,) = result.inserted_primary_key

    activation_instance_id = int(data.get("ansible_rulebook_id"))
    query = insert(models.activation_instance_job_instances).values(
        job_instance_id=job_instance_id,
        activation_instance_id=activation_instance_id,
    )
    await db.execute(query)
    await db.commit()
    await updatemanager.broadcast(
        f"/activation_instance/{activation_instance_id}",
        json.dumps(["Job", {"job_instance_id": job_instance_id}]),
    )
    await updatemanager.broadcast(
        "/jobs",
        json.dumps(["Job", {"id": job_instance_id}]),
    )


async def handle_actions(data: dict, db: AsyncSession):
    logger.info(f"Start to handle actions: {data}")
    activation_id = int(data.get("activation_id"))

    if activation_id:
        action_name = data.get("action")
        playbook_name = data.get("playbook_name")
        job_id = data.get("job_id")
        fired_date = datetime.strptime(
            data.get("run_at"), "%Y-%m-%d %H:%M:%S.%f"
        )
        status = data.get("status")

        if job_id:
            sel = (
                select(
                    models.activation_instances.c.id.label(
                        "activation_instance_id"
                    ),
                    models.rulesets.c.id.label("ruleset_id"),
                    models.rules.c.id.label("rule_id"),
                    models.rules.c.name,
                    models.rules.c.action.label("definition"),
                    models.job_instances.c.id.label("job_instance_id"),
                    cast(fired_date, postgresql.TIMESTAMP).label("fired_date"),
                    cast(status, postgresql.VARCHAR).label("status"),
                )
                .join(
                    models.rulesets,
                    models.rulesets.c.rulebook_id
                    == models.activation_instances.c.rulebook_id,
                )
                .join(
                    models.rules,
                    models.rules.c.ruleset_id == models.rulesets.c.id,
                )
                .join(
                    models.job_instances,
                    models.job_instances.c.uuid
                    == cast(job_id, postgresql.UUID),
                )
                .where(
                    models.activation_instances.c.id == activation_id,
                    models.rules.c.action[action_name].is_not(None),
                    models.rules.c.action[action_name]["name"].astext
                    == playbook_name,
                    models.job_instances.c.id.is_not(None),
                )
            )
            ins_cols = [
                "activation_instance_id",
                "ruleset_id",
                "rule_id",
                "name",
                "definition",
                "job_instance_id",
                "fired_date",
                "status",
            ]
        else:
            sel = (
                select(
                    models.activation_instances.c.id.label(
                        "activation_instance_id"
                    ),
                    models.rulesets.c.id.label("ruleset_id"),
                    models.rules.c.id.label("rule_id"),
                    models.rules.c.name,
                    models.rules.c.action.label("definition"),
                    cast(fired_date, postgresql.TIMESTAMP).label("fired_date"),
                    cast(status, postgresql.VARCHAR).label("status"),
                )
                .join(
                    models.rulesets,
                    models.rulesets.c.rulebook_id
                    == models.activation_instances.c.rulebook_id,
                )
                .join(
                    models.rules,
                    models.rules.c.ruleset_id == models.rulesets.c.id,
                )
                .where(
                    models.activation_instances.c.id == activation_id,
                    models.rules.c.action[action_name].is_not(None),
                    models.rules.c.action[action_name]["name"].astext
                    == playbook_name,
                )
            )
            ins_cols = [
                "activation_instance_id",
                "ruleset_id",
                "rule_id",
                "name",
                "definition",
                "fired_date",
                "status",
            ]

        ins = insert(models.audit_rules).from_select(ins_cols, sel)
        # End build insert-from-select query

        await db.execute(ins)
        await db.commit()
