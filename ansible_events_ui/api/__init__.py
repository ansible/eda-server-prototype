import asyncio
import base64
import json
import logging
import uuid
from typing import List

import aiodocker.exceptions
import sqlalchemy.orm
import yaml
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui import schemas
from ansible_events_ui.config import Settings, get_settings
from ansible_events_ui.db import models
from ansible_events_ui.db.dependency import (
    get_db_session,
    get_db_session_factory,
)
from ansible_events_ui.key import generate_ssh_keys
from ansible_events_ui.db.utils.lostream import large_object_factory
from ansible_events_ui.managers import (
    secretsmanager,
    taskmanager,
    updatemanager,
)
from ansible_events_ui.project import insert_rulebook_related_data
from ansible_events_ui.ruleset import (
    activate_rulesets,
    inactivate_rulesets,
    run_job,
    write_job_events,
)
from ansible_events_ui.users import (
    bearer_backend,
    cookie_backend,
    current_active_user,
    fastapi_users,
)

from .activation import router as activation_router
from .project import router as project_router
from .rule import router as rule_router

logger = logging.getLogger("ansible_events_ui")

router = APIRouter()
router.include_router(activation_router)
router.include_router(rule_router)
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


@router.post("/api/rulebooks/")
async def create_rulebook(
    rulebook: schemas.Rulebook, db: AsyncSession = Depends(get_db_session)
):
    query = insert(models.rulebooks).values(
        name=rulebook.name, rulesets=rulebook.rulesets
    )
    result = await db.execute(query)
    (id_,) = result.inserted_primary_key

    rulebook_data = yaml.safe_load(rulebook.rulesets)
    await insert_rulebook_related_data(id_, rulebook_data, db)
    await db.commit()

    return {**rulebook.dict(), "id": id_}


@router.post("/api/inventory/")
async def create_inventory(
    i: schemas.Inventory, db: AsyncSession = Depends(get_db_session)
):
    query = insert(models.inventories).values(
        name=i.name, inventory=i.inventory
    )
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**i.dict(), "id": id_}


@router.post("/api/extra_vars/")
async def create_extra_vars(
    e: schemas.Extravars, db: AsyncSession = Depends(get_db_session)
):
    query = insert(models.extra_vars).values(
        name=e.name, extra_var=e.extra_var
    )
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**e.dict(), "id": id_}


@router.post("/api/activation_instance/")
async def create_activation_instance(
    a: schemas.ActivationInstance,
    db: AsyncSession = Depends(get_db_session),
    db_session_factory: sqlalchemy.orm.sessionmaker = Depends(
        get_db_session_factory
    ),
    settings: Settings = Depends(get_settings),
):
    query = (
        select(
            inventories.c.inventory,
            rulebooks.c.rulesets,
            extra_vars.c.extra_var
        ).join(inventories, activations.c.inventory_id == inventories.c.id)
        .join(rulebooks, activations.c.rulebook_id == rulebooks.c.id)
        .join(extra_vars, activations.c.extra_var_id == extra_vars.c.id)
        .where(activations.c.id == activation.id)
    )
    activation_data = (await db.execute(query)).first()

    query = insert(models.activation_instances).values(
        name=a.name,
        rulebook_id=a.rulebook_id,
        inventory_id=a.inventory_id,
        extra_var_id=a.extra_var_id,
        working_directory=a.working_directory,
        execution_environment=a.execution_environment,
    ).returning(
        activation_instances.c.id,
        activation_instances.c.log_id,
    )
    result = await db.execute(query)
    await db.commit()
    id_, log_id = result.first()

    try:
        await activate_rulesets(
            settings.deployment_type,
            id_,
            log_id,
            a.execution_environment,
            activation_data.rulesets,
            activation_data.inventory,
            activation_data.extra_var,
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


@router.get(
    "/api/activation_instance_logs/",
    response_model=List[schemas.ActivationLog],
)
async def list_activation_instance_logs(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        select(activation_instances.c.log_id).where(activation_instances.c.id == activation_instance_id)
    )
    rec = (await db.execute(query)).first()
    if rec is None:
        raise HTTPException(status_code=404, detail=f"Activation instance id {activation_instance_id} not found")

    # Open the large object and decode bytes to text via "utf-8"  (mode="rt")
    try:
        lobject = await large_object_factory(oid=rec.log_id, session=db, mode="rt")
    except FileNotFoundError as lob_exc:
        raise HTTPException(status_code=404, detail=str(lob_exc))

    async for buff in lobject.gread():
        await updatemanager.broadcast(
            f"/activation_instance/{activation_instance_id}",
            json.dumps(["Stdout", {"stdout": buff}]),
        )

    return []


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


@router.get("/api/playbooks/")
async def list_playbooks(db: AsyncSession = Depends(get_db_session)):
    query = select(models.playbooks)
    result = await db.execute(query)
    return result.all()


@router.get("/api/playbook/{playbook_id}")
async def read_playbook(
    playbook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(models.playbooks).where(
        models.playbooks.c.id == playbook_id
    )
    result = await db.execute(query)
    return result.first()


@router.get("/api/inventories/")
async def list_inventories(db: AsyncSession = Depends(get_db_session)):
    query = select(models.inventories)
    result = await db.execute(query)
    return result.all()


@router.get("/api/inventory/{inventory_id}")
async def read_inventory(
    inventory_id: int, db: AsyncSession = Depends(get_db_session)
):
    # FIXME(cutwater): Return HTTP 404 if inventory doesn't exist
    query = select(models.inventories).where(
        models.inventories.c.id == inventory_id
    )
    result = await db.execute(query)
    return result.first()


@router.get("/api/rulebooks/")
async def list_rulebooks(db: AsyncSession = Depends(get_db_session)):
    query = select(models.rulebooks)
    result = await db.execute(query)
    return result.all()


@router.get("/api/rulebooks/{rulebook_id}")
async def read_rulebook(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(models.rulebooks).where(
        models.rulebooks.c.id == rulebook_id
    )
    result = await db.execute(query)
    return result.first()


@router.get("/api/rulebook_json/{rulebook_id}")
async def read_rulebook_json(
    rulebook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(models.rulebooks).where(
        models.rulebooks.c.id == rulebook_id
    )
    result = await db.execute(query)

    response = dict(result.first())
    response["rulesets"] = yaml.safe_load(response["rulesets"])
    return response


@router.get("/api/extra_vars/")
async def list_extra_vars(db: AsyncSession = Depends(get_db_session)):
    query = select(models.extra_vars)
    result = await db.execute(query)
    return result.all()


@router.get("/api/extra_var/{extra_var_id}")
async def read_extravar(
    extra_var_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(models.extra_vars).where(
        models.extra_vars.c.id == extra_var_id
    )
    result = await db.execute(query)
    return result.first()


@router.get("/api/activation_instances/")
async def list_activation_instances(
    db: AsyncSession = Depends(get_db_session),
):
    query = select(models.activation_instances)
    result = await db.execute(query)
    return result.all()


@router.get("/api/activation_instance/{activation_instance_id}")
async def read_activation_instance(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        select(
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
    status_code=204,
    operation_id="delete_activation_instance",
)
async def delete_activation_instance(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = delete(models.activation_instances).where(
        models.activation_instances.c.id == activation_instance_id
    )
    results = await db.execute(query)
    if results.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.commit()


@router.get("/api/job_instances/")
async def list_job_instances(db: AsyncSession = Depends(get_db_session)):
    query = select(models.job_instances)
    result = await db.execute(query)
    return result.all()


@router.post("/api/job_instance/")
async def create_job_instance(
    j: schemas.JobInstance, db: AsyncSession = Depends(get_db_session)
):

    query = select(models.playbooks).where(
        models.playbooks.c.id == j.playbook_id
    )
    playbook_row = (await db.execute(query)).first()

    query = select(models.inventories).where(
        models.inventories.c.id == j.inventory_id
    )
    inventory_row = (await db.execute(query)).first()

    query = select(models.extra_vars).where(
        models.extra_vars.c.id == j.extra_var_id
    )
    extra_var_row = (await db.execute(query)).first()

    job_uuid = str(uuid.uuid4())

    query = insert(models.job_instances).values(uuid=job_uuid)
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


@router.get("/api/job_instance/{job_instance_id}")
async def read_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(models.job_instances).where(
        models.job_instances.c.id == job_instance_id
    )
    result = await db.execute(query)
    return result.first()


@router.delete(
    "/api/job_instance/{job_instance_id}",
    status_code=204,
    operation_id="delete_job_instance",
)
async def delete_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = delete(models.job_instances).where(
        models.job_instances.c.id == job_instance_id
    )
    results = await db.execute(query)
    if results.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.commit()


@router.get("/api/job_instance_events/{job_instance_id}")
async def read_job_instance_events(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(models.job_instances).where(
        models.job_instances.c.id == job_instance_id
    )
    job = (await db.execute(query)).first()

    query = (
        select(models.job_instance_events)
        .where(models.job_instance_events.c.job_uuid == job.uuid)
        .order_by(models.job_instance_events.c.counter)
    )
    return (await db.execute(query)).all()


@router.get("/api/activation_instance_job_instances/{activation_instance_id}")
async def read_activation_instance_job_instances(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(models.activation_instance_job_instances).where(
        models.activation_instance_job_instances.c.activation_instance_id
        == activation_instance_id
    )
    result = await db.execute(query)
    return result.all()


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
