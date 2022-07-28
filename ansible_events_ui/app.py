import asyncio
import json
from collections import defaultdict
from typing import List

import yaml
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .db.models import (
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
from .db.session import async_session_maker, get_db_session
from .manager import activate_rulesets, inactivate_rulesets
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


# TODO(cutwater): A more reliable, scalable and robust tasking system
#   is probably needed.
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
    websocket: WebSocket, db: AsyncSession = Depends(get_db_session)
):
    print("starting ws2")
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            print(data)
            # TODO(cutwater): Some data validation is needed
            data_type = data.get("type")
            if data_type == "Job":
                query = insert(job_instances).values(uuid=data.get("job_id"))
                result = await db.execute(query)
                (job_instance_id,) = result.inserted_primary_key

                activation_instance_id = int(data.get("ansible_events_id"))
                query = insert(activation_instance_job_instances).values(
                    job_instance_id=job_instance_id,
                    activation_instance_id=activation_instance_id,
                )
                await db.execute(query)
                await db.commit()
                await updatemanager.broadcast(
                    f"/activation_instance/{activation_instance_id}",
                    json.dumps(["Job", {"id": job_instance_id}]),
                )
            elif data_type == "AnsibleEvent":
                event_data = data.get("event", {})
                query = insert(job_instance_events).values(
                    job_uuid=event_data.get("job_id"),
                    counter=event_data.get("counter"),
                    stdout=event_data.get("stdout"),
                )
                await db.execute(query)
                await db.commit()
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
    rsf: RuleSetFile, db: AsyncSession = Depends(get_db_session)
):
    query = insert(rule_set_files).values(name=rsf.name, rulesets=rsf.rulesets)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**rsf.dict(), "id": id_}


@app.post("/api/inventory/")
async def create_inventory(
    i: Inventory, db: AsyncSession = Depends(get_db_session)
):
    query = insert(inventories).values(name=i.name, inventory=i.inventory)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**i.dict(), "id": id_}


@app.post("/api/extra_vars/")
async def create_extra_vars(
    e: Extravars, db: AsyncSession = Depends(get_db_session)
):
    query = insert(extra_vars).values(name=e.name, extra_var=e.extra_var)
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key
    return {**e.dict(), "id": id_}


@app.post("/api/activation_instance/")
async def create_activation_instance(
    a: Activation, db: AsyncSession = Depends(get_db_session)
):
    query = select(rule_set_files).where(
        rule_set_files.c.id == a.rule_set_file_id
    )
    rule_set_file_row = (await db.execute(query)).first()

    query = select(inventories).where(inventories.c.id == a.inventory_id)
    inventory_row = (await db.execute(query)).first()

    query = select(extra_vars).where(extra_vars.c.id == a.extra_var_id)
    extra_var_row = (await db.execute(query)).first()

    query = insert(activation_instances).values(
        name=a.name,
        rule_set_file_id=a.rule_set_file_id,
        inventory_id=a.inventory_id,
        extra_var_id=a.extra_var_id,
    )
    result = await db.execute(query)
    await db.commit()
    (id_,) = result.inserted_primary_key

    cmd, proc = await activate_rulesets(
        id_,
        # TODO(cutwater): Hardcoded container image link
        "quay.io/bthomass/ansible-events:latest",
        rule_set_file_row.rulesets,
        inventory_row.inventory,
        extra_var_row.extra_var,
        db,
    )

    task = asyncio.create_task(
        read_output(proc, id_), name=f"read_output {proc.pid}"
    )
    taskmanager.tasks.append(task)

    return {**a.dict(), "id": id_}


@app.post("/api/deactivate/")
async def deactivate(activation_instance_id: int):
    await inactivate_rulesets(activation_instance_id)
    return


async def read_output(proc, activation_instance_id):
    # TODO(cutwater): Replace with FastAPI dependency injections,
    #   that is available in BackgroundTasks
    async with async_session_maker() as db:
        line_number = 0
        # FIXME(cutwater): The `done` variable is never set to True.
        done = False
        while not done:
            line = await proc.stdout.readline()
            if len(line) == 0:
                break
            line = line.decode()
            # FIXME(cutwater): F-string is not needed here
            print(f"{line}", end="")
            query = insert(activation_instance_logs).values(
                line_number=line_number,
                log=line,
                activation_instance_id=activation_instance_id,
            )
            await db.execute(query)
            await db.commit()
            line_number += 1
            await connnectionmanager.broadcast(
                json.dumps(["Stdout", {"stdout": line}])
            )


@app.get("/api/activation_instance_logs/", response_model=List[ActivationLog])
async def list_activation_instance_logs(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
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
        {
            "name": task.get_name(),
            "done": task.done(),
            "cancelled": task.cancelled(),
        }
        for task in taskmanager.tasks
    ]
    return tasks


@app.post("/api/project/")
async def create_project(
    p: Project, db: AsyncSession = Depends(get_db_session)
):
    found_hash, tempdir = await clone_project(p.url, p.git_hash)
    p.git_hash = found_hash
    query = insert(projects).values(url=p.url, git_hash=p.git_hash)
    result = await db.execute(query)
    (project_id,) = result.inserted_primary_key
    await sync_project(project_id, tempdir, db)
    await db.commit()
    return {**p.dict(), "id": project_id}


@app.get("/api/project/{project_id}")
async def read_project(
    project_id: int, db: AsyncSession = Depends(get_db_session)
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
async def list_projects(db: AsyncSession = Depends(get_db_session)):
    query = select(projects)
    result = await db.execute(query)
    return result.all()


@app.get("/api/playbooks/")
async def list_playbooks(db: AsyncSession = Depends(get_db_session)):
    query = select(playbooks)
    result = await db.execute(query)
    return result.all()


@app.get("/api/playbook/{playbook_id}")
async def read_playbook(
    playbook_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(playbooks).where(playbooks.c.id == playbook_id)
    result = await db.execute(query)
    return result.first()


@app.get("/api/inventories/")
async def list_inventories(db: AsyncSession = Depends(get_db_session)):
    query = select(inventories)
    result = await db.execute(query)
    return result.all()


@app.get("/api/inventory/{inventory_id}")
async def read_inventory(
    inventory_id: int, db: AsyncSession = Depends(get_db_session)
):
    # FIXME(cutwater): Return HTTP 404 if inventory doesn't exist
    query = select(inventories).where(inventories.c.id == inventory_id)
    result = await db.execute(query)
    return result.first()


@app.get("/api/rule_set_files/")
async def list_rule_set_files(db: AsyncSession = Depends(get_db_session)):
    query = select(rule_set_files)
    result = await db.execute(query)
    return result.all()


@app.get("/api/rule_set_file/{rule_set_file_id}")
async def read_rule_set_file(
    rule_set_file_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(rule_set_files).where(
        rule_set_files.c.id == rule_set_file_id
    )
    result = await db.execute(query)
    return result.first()


@app.get("/api/rule_set_file_json/{rule_set_file_id}")
async def read_rule_set_file_json(
    rule_set_file_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(rule_set_files).where(
        rule_set_files.c.id == rule_set_file_id
    )
    result = await db.execute(query)

    response = dict(result.first())
    response["rulesets"] = yaml.safe_load(response["rulesets"])
    return response


@app.get("/api/extra_vars/")
async def list_extra_vars(db: AsyncSession = Depends(get_db_session)):
    query = select(extra_vars)
    result = await db.execute(query)
    return result.all()


@app.get("/api/extra_var/{extra_var_id}")
async def read_extravar(
    extra_var_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(extra_vars).where(extra_vars.c.id == extra_var_id)
    result = await db.execute(query)
    return result.first()


@app.get("/api/activation_instances/")
async def list_activation_instances(
    db: AsyncSession = Depends(get_db_session),
):
    query = select(activation_instances)
    result = await db.execute(query)
    return result.all()


@app.get("/api/activation_instance/{activation_instance_id}")
async def read_activation_instance(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
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
async def list_job_instances(db: AsyncSession = Depends(get_db_session)):
    query = select(job_instances)
    result = await db.execute(query)
    return result.all()


@app.get("/api/job_instance/{job_instance_id}")
async def read_job_instance(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(job_instances).where(job_instances.c.id == job_instance_id)
    result = await db.execute(query)
    return result.first()


@app.get("/api/job_instance_events/{job_instance_id}")
async def read_job_instance_events(
    job_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = select(job_instances).where(job_instances.c.id == job_instance_id)
    job = (await db.execute(query)).first()

    query = select(job_instance_events).where(
        job_instance_events.c.job_uuid == job.uuid
    )
    return (await db.execute(query)).all()


@app.get("/api/activation_instance_job_instances/{activation_instance_id}")
async def read_activation_instance_job_instances(
    activation_instance_id: int, db: AsyncSession = Depends(get_db_session)
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
