import base64
import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schemas
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import get_db_session
from ansible_events_ui.key import generate_ssh_keys
from ansible_events_ui.db.utils.lostream import large_object_factory
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
                await websocket.send_text(json.dumps({"type": "Hello"}))
                query = select(models.activation_instances).where(
                    models.activation_instances.c.id
                    == data.get("activation_id")
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
                                    secretsmanager.get_secret(
                                        "ssh-private-key"
                                    ).encode()
                                ).decode(),
                            }
                        )
                    )
                else:
                    await websocket.send_text(
                        json.dumps({"type": "SSHPrivateKey", "data": ""})
                    )

            elif data_type == "Job":
                query = insert(models.job_instances).values(
                    uuid=data.get("job_id")
                )
                result = await db.execute(query)
                (job_instance_id,) = result.inserted_primary_key

                activation_instance_id = int(data.get("ansible_events_id"))
                query = insert(
                    models.activation_instance_job_instances
                ).values(
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
            elif data_type == "AnsibleEvent":
                event_data = data.get("event", {})
                if event_data.get("stdout"):
                    query = select(models.job_instances).where(
                        models.job_instances.c.uuid == event_data.get("job_id")
                    )
                    result = await db.execute(query)
                    job_instance_id = result.first().job_instance_id

                    await updatemanager.broadcast(
                        f"/job_instance/{job_instance_id}",
                        json.dumps(
                            ["Stdout", {"stdout": event_data.get("stdout")}]
                        ),
                    )

                query = insert(models.job_instance_events).values(
                    job_uuid=event_data.get("job_id"),
                    counter=event_data.get("counter"),
                    stdout=event_data.get("stdout"),
                )
                await db.execute(query)
                await db.commit()
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
