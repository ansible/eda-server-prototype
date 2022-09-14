import base64
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import cast, insert, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schemas
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.key import generate_ssh_keys
from ansible_events_ui.managers import (
    secretsmanager,
    taskmanager,
    updatemanager,
)
from ansible_events_ui.users import (
    bearer_backend,
    cookie_backend,
    current_active_user,
    fastapi_users,
)

from .activation import router as activation_router
from .job import router as job_router
from .project import router as project_router
from .rulebook import router as rulebook_router

logger = logging.getLogger("ansible_events_ui")

router = APIRouter()
router.include_router(activation_router)
router.include_router(job_router)
router.include_router(rulebook_router)
router.include_router(project_router)


@router.websocket("/api/ws2")
async def websocket_endpoint2(
    websocket: WebSocket, db: AsyncSession = Depends(get_db_session)
):
    logger.debug("starting ws2")
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            # TODO(cutwater): Some data validation is needed
            data_type = data.get("type")
            if data_type == "Worker":
                await handle_workers(websocket, data, db)
            elif data_type == "Job":
                await handle_jobs(data, db)
            elif data_type == "AnsibleEvent":
                await handle_ansible_events(data, db)
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


@router.websocket("/api/ws-jobs/")
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


async def handle_workers(websocket: WebSocket, data: dict, db: AsyncSession):
    await websocket.send_text(json.dumps({"type": "Hello"}))
    query = select(models.activation_instances).where(
        models.activation_instances.c.id == data.get("activation_id")
    )
    activation = (await db.execute(query)).first()

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


async def handle_ansible_events(data: dict, db: AsyncSession):
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
    await db.commit()


async def handle_jobs(data: dict, db: AsyncSession):
    query = insert(models.job_instances).values(uuid=data.get("job_id"))
    result = await db.execute(query)
    (job_instance_id,) = result.inserted_primary_key

    activation_instance_id = int(data.get("ansible_events_id"))
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


@router.get("/api/tasks/")
async def list_tasks():
    tasks = [
        {
            "name": task.get_name(),
            "done": task.done(),
            "cancelled": task.cancelled(),
        }
        for task in taskmanager.tasks
    ]
    return tasks


# FastAPI Users


router.include_router(
    fastapi_users.get_auth_router(cookie_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_auth_router(bearer_backend),
    prefix="/api/auth/bearer",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(schemas.UserRead),
    prefix="/api/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
    prefix="/api/users",
    tags=["users"],
)


@router.get("/api/authenticated-route")
async def authenticated_route(
    user: models.User = Depends(current_active_user),
):
    return {"message": f"Hello {user.email}!"}


@router.get("/api/ssh-public-key")
async def ssh_public_key():
    if secretsmanager.has_secret("ssh-public-key"):
        return {"public_key": secretsmanager.get_secret("ssh-public-key")}
    else:
        ssh_private_key, ssh_public_key = await generate_ssh_keys()
        secretsmanager.set_secret("ssh-public-key", ssh_public_key)
        secretsmanager.set_secret("ssh-private-key", ssh_private_key)
        return {"public_key": secretsmanager.get_secret("ssh-public-key")}
