import asyncio
import json
from collections import defaultdict
from typing import List

import yaml
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import database, get_async_session
from .manager import activate_rulesets, inactivate_rulesets
from .models import (
    User,
    activation_instance_job_instances,
    activation_instance_logs,
    activation_instances,
    extra_vars,
    inventories,
    job_instance_events,
    job_instances,
    playbooks,
    project_inventories,
    project_playbooks,
    project_rules,
    project_vars,
    projects,
    rule_set_files,
)
from .project import clone_project, sync_project
from .schemas import (
    Activation,
    ActivationLog,
    Extravars,
    Inventory,
    Project,
    RuleSetFile,
    UserCreate,
    UserRead,
    UserUpdate,
)
from .users import auth_backend, current_active_user, fastapi_users

app = FastAPI(title="Ansible Events API")

app.mount("/eda", StaticFiles(directory="ui/dist", html=True), name="eda")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:9000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskManager:
    def __init__(self):

        self.tasks = []


taskmanager = TaskManager()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


connnectionmanager = ConnectionManager()


class UpdateManager:
    def __init__(self):
        self.active_connections = defaultdict(list)

    async def connect(self, page, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[page].append(websocket)
        print("connect", page, self.active_connections[page])

    def disconnect(self, page, websocket: WebSocket):
        self.active_connections[page].remove(websocket)

    async def broadcast(self, page, message: str):
        print("broadcast", page, message, "->", self.active_connections[page])
        for connection in self.active_connections[page]:
            await connection.send_text(message)


updatemanager = UpdateManager()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return RedirectResponse("/eda")


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("starting ws")
    await connnectionmanager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        connnectionmanager.disconnect(websocket)


@app.websocket("/api/ws2")
async def websocket_endpoint2(
    websocket: WebSocket, db: AsyncSession = Depends(get_async_session)
):
    print("starting ws2")
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            print(data)
            data_type = data.get("type")
            if data_type == "Job":
                query = job_instances.insert().values(uuid=data.get("job_id"))
                last_record_id = await database.execute(query)
                activation_instance_id = int(data.get("ansible_events_id"))
                query = activation_instance_job_instances.insert().values(
                    job_instance_id=last_record_id,
                    activation_instance_id=activation_instance_id,
                )
                await database.execute(query)
                await updatemanager.broadcast(
                    f"/activation_instance/{activation_instance_id}",
                    json.dumps(["Job", dict(id=last_record_id)]),
                )
            elif data_type == "AnsibleEvent":
                event_data = data.get("event", {})
                query = job_instance_events.insert().values(
                    job_uuid=event_data.get("job_id"),
                    counter=event_data.get("counter"),
                    stdout=event_data.get("stdout"),
                )
                await database.execute(query)
            print(data)
    except WebSocketDisconnect:
        pass


@app.websocket("/api/ws-activation/{activation_instance_id}")
async def websocket_activation_endpoint(
    websocket: WebSocket, activation_instance_id
):
    page = f"/activation_instance/{activation_instance_id}"
    await updatemanager.connect(page, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
    except WebSocketDisconnect:
        updatemanager.disconnect(page, websocket)


@app.get("/ping")
def ping():
    return {"ping": "pong!"}


@app.post("/api/rule_set_file/")
async def create_rule_set_file(
    rsf: RuleSetFile, db: AsyncSession = Depends(get_async_session)
):
    query = rule_set_files.insert().values(
        name=rsf.name, rulesets=rsf.rulesets
    )
    last_record_id = await database.execute(query)
    return {**rsf.dict(), "id": last_record_id}


@app.post("/api/inventory/")
async def create_inventory(
    i: Inventory, db: AsyncSession = Depends(get_async_session)
):
    query = inventories.insert().values(name=i.name, inventory=i.inventory)
    last_record_id = await database.execute(query)
    return {**i.dict(), "id": last_record_id}


@app.post("/api/extra_vars/")
async def create_extra_vars(
    e: Extravars, db: AsyncSession = Depends(get_async_session)
):
    query = extra_vars.insert().values(name=e.name, extra_vars=e.extra_vars)
    last_record_id = await database.execute(query)
    return {**e.dict(), "id": last_record_id}


@app.post("/api/activation_instance/")
async def create_activation_instance(
    a: Activation, db: AsyncSession = Depends(get_async_session)
):
    query = rule_set_files.select().where(
        rule_set_files.c.id == a.rule_set_file_id
    )
    r = await database.fetch_one(query)
    query = inventories.select().where(inventories.c.id == a.inventory_id)
    i = await database.fetch_one(query)
    query = extra_vars.select().where(extra_vars.c.id == a.extra_var_id)
    e = await database.fetch_one(query)
    query = activation_instances.insert().values(
        name=a.name,
        rule_set_file_id=a.rule_set_file_id,
        inventory_id=a.inventory_id,
        extra_var_id=a.extra_var_id,
    )
    last_record_id = await database.execute(query)
    cmd, proc = await activate_rulesets(
        last_record_id,
        # FIXME(cutwater): Hardcoded container image link
        "quay.io/bthomass/ansible-events:latest",
        r.rulesets,
        i.inventory,
        e.extra_var,
    )

    task1 = asyncio.create_task(
        read_output(proc, last_record_id), name=f"read_output {proc.pid}"
    )
    taskmanager.tasks.append(task1)

    return {**a.dict(), "id": last_record_id}


@app.post("/api/deactivate/")
async def deactivate(activation_instance_id: int):
    await inactivate_rulesets(activation_instance_id)
    return


# TODO(cutwater): This method is executed as a background task.
#  It must create database session.
async def read_output(proc, activation_instance_id):
    line_number = 0
    done = False
    while not done:
        line = await proc.stdout.readline()
        if len(line) == 0:
            break
        line = line.decode()
        # FIXME(cutwater): F-string is not needed here
        print(f"{line}", end="")
        query = activation_instance_logs.insert().values(
            line_number=line_number,
            log=line,
            activation_instance_id=activation_instance_id,
        )
        await database.execute(query)
        line_number += 1
        await connnectionmanager.broadcast(
            json.dumps(["Stdout", dict(stdout=line)])
        )


@app.get("/api/activation_instance_logs/", response_model=List[ActivationLog])
async def list_activation_instance_logs(
    activation_instance_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = select(activation_instance_logs).where(
        activation_instance_logs.c.activation_instance_id
        == activation_instance_id
    )
    result = await db.execute(query)
    return result.all()


@app.get("/api/tasks/")
async def list_tasks():
    tasks = [
        dict(
            name=task.get_name(), done=task.done(), cancelled=task.cancelled()
        )
        for task in taskmanager.tasks
    ]
    return tasks


@app.post("/api/project/")
async def create_project(
    p: Project, db: AsyncSession = Depends(get_async_session)
):
    found_hash, tempdir = await clone_project(p.url, p.git_hash)
    p.git_hash = found_hash
    query = projects.insert().values(url=p.url, git_hash=p.git_hash)
    last_record_id = await database.execute(query)
    await sync_project(last_record_id, tempdir)
    return {**p.dict(), "id": last_record_id}


@app.get("/api/project/{project_id}")
async def read_project(
    project_id: int, db: AsyncSession = Depends(get_async_session)
):
    # FIXME(cutwater): Return HTTP 404 if project doesn't exist
    query = select(projects).where(projects.c.id == project_id)
    project = (await db.execute(query)).first()

    response = dict(project)

    response["rulesets"] = (
        await db.execute(
            select(rule_set_files.c.id, rule_set_files.c.name)
            .select_from(projects.join(project_rules).join(rule_set_files))
            .where(projects.c.id == project_id)
        )
    ).all()

    response["inventories"] = (
        await db.execute(
            select(inventories.c.id, inventories.c.name)
            .select_from(projects.join(project_inventories).join(inventories))
            .where(projects.c.id == project_id)
        )
    ).all()

    response["vars"] = (
        await db.execute(
            select(extra_vars.c.id, extra_vars.c.name)
            .select_from(projects.join(project_vars).join(extra_vars))
            .where(projects.c.id == project_id)
        )
    ).all()

    response["playbooks"] = (
        await db.execute(
            select(playbooks.c.id, playbooks.c.name)
            .select_from(projects.join(project_playbooks).join(playbooks))
            .where(projects.c.id == project_id)
        )
    ).all()

    return response


@app.get("/api/projects/")
async def list_projects(db: AsyncSession = Depends(get_async_session)):
    query = select(projects)
    result = await db.execute(query)
    return result.all()


@app.get("/api/playbooks/")
async def list_playbooks(db: AsyncSession = Depends(get_async_session)):
    query = select(playbooks)
    result = await db.execute(query)
    return result.all()


@app.get("/api/playbook/{playbook_id}")
async def read_playbook(
    playbook_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = select(playbooks).where(playbooks.c.id == playbook_id)
    result = await db.execute(query)
    return result.first()


@app.get("/api/inventories/")
async def list_inventories(db: AsyncSession = Depends(get_async_session)):
    query = select(inventories)
    result = await db.execute(query)
    return result.all()


@app.get("/api/inventory/{inventory_id}")
async def read_inventory(
    inventory_id: int, db: AsyncSession = Depends(get_async_session)
):
    # FIXME(cutwater): Return HTTP 404 if inventory doesn't exist
    query = select(inventories).where(inventories.c.id == inventory_id)
    result = await db.execute(query)
    return result.first()


@app.get("/api/rule_set_files/")
async def list_rule_set_files(db: AsyncSession = Depends(get_async_session)):
    query = rule_set_files.select()
    return await database.fetch_all(query)


@app.get("/api/rule_set_file/{rule_set_file_id}")
async def read_rule_set_file(
    rule_set_file_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = rule_set_files.select().where(
        rule_set_files.c.id == rule_set_file_id
    )
    return await database.fetch_one(query)


@app.get("/api/rule_set_file_json/{rule_set_file_id}")
async def read_rule_set_file_json(
    rule_set_file_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = select(rule_set_files).where(
        rule_set_files.c.id == rule_set_file_id
    )
    result = await db.execute(query)

    response = dict(result.first())
    response["rulesets"] = yaml.safe_load(response["rulesets"])
    return response


@app.get("/api/extra_vars/")
async def list_extra_vars(db: AsyncSession = Depends(get_async_session)):
    query = select(extra_vars)
    result = await db.execute(query)
    return result.all()


@app.get("/api/extra_var/{extra_var_id}")
async def read_extravar(
    extra_var_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = select(extra_vars).where(extra_vars.c.id == extra_var_id)
    result = await db.execute(query)
    return result.first()


@app.get("/api/activation_instances/")
async def list_activation_instances(
    db: AsyncSession = Depends(get_async_session),
):
    query = select(activation_instances)
    result = await db.execute(query)
    return result.all()


@app.get("/api/activation_instance/{activation_instance_id}")
async def read_activation_instance(
    activation_instance_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = (
        select(
            activation_instances.c.id,
            activation_instances.c.name,
            rule_set_files.c.id.label("ruleset_id"),
            rule_set_files.c.name.label("ruleset_name"),
            inventories.c.id.label("inventory_id"),
            inventories.c.name.label("inventory_name"),
            extra_vars.c.id.label("extra_var_id"),
            extra_vars.c.name.label("extra_vars_name"),
        )
        .select_from(
            activation_instances.join(rule_set_files)
            .join(inventories)
            .join(extra_vars)
        )
        .where(activation_instances.c.id == activation_instance_id)
    )
    result = await db.execute(query)
    return result.first()


@app.get("/api/job_instances/")
async def list_job_instances(db: AsyncSession = Depends(get_async_session)):
    query = select(job_instances)
    result = await db.execute(query)
    return result.all()


@app.get("/api/job_instance/{job_instance_id}")
async def read_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = select(job_instances).where(job_instances.c.id == job_instance_id)
    result = await db.execute(query)
    return result.all()


@app.get("/api/job_instance_events/{job_instance_id}")
async def read_job_instance_events(
    job_instance_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = select(job_instances).where(job_instances.c.id == job_instance_id)
    job = (await db.execute(query)).first()

    query = select(job_instance_events).where(
        job_instance_events.c.job_uuid == job.uuid
    )
    return (await db.execute(query)).all()


@app.get("/api/activation_instance_job_instances/{activation_instance_id}")
async def read_activation_instance_job_instances(
    activation_instance_id: int, db: AsyncSession = Depends(get_async_session)
):
    query = select(activation_instance_job_instances).where(
        activation_instance_job_instances.c.activation_instance_id
        == activation_instance_id
    )
    result = await db.execute(query)
    return result.all()


# FastAPI Users


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["users"],
)


@app.get("/api/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
