from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
from collections import defaultdict
from sqlalchemy import select
from .schemas import RuleSetFile, Inventory, Activation, ActivationLog, Extravars
from .schemas import Project
from .models import (
    rulesetfiles,
    inventories,
    extravars,
    activations,
    activation_logs,
    projects,
    playbooks,
    jobs,
    job_events,
    activationjobs,
    projectrules,
    projectinventories,
    projectvars,
    projectplaybooks,
)
from .manager import activate_rulesets, inactivate_rulesets
from .project import clone_project, sync_project
from .database import database
import json
import yaml

from .models import User
from .schemas import UserCreate, UserRead, UserUpdate
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
    print('starting ws')
    await connnectionmanager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        connnectionmanager.disconnect(websocket)


@app.websocket("/api/ws2")
async def websocket_endpoint2(websocket: WebSocket):
    print('starting ws2')
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            print(data)
            data_type = data.get("type")
            if data_type == "Job":
                query = jobs.insert().values(uuid=data.get("job_id"))
                last_record_id = await database.execute(query)
                activation_id = int(data.get("ansible_events_id"))
                query = activationjobs.insert().values(
                    job_id=last_record_id,
                    activation_id=activation_id,
                )
                await database.execute(query)
                await updatemanager.broadcast(
                    f"/activation/{activation_id}",
                    json.dumps(["Job", dict(id=last_record_id)]),
                )
            elif data_type == "AnsibleEvent":
                event_data = data.get("event", {})
                query = job_events.insert().values(
                    job_uuid=event_data.get("job_id"),
                    counter=event_data.get("counter"),
                    stdout=event_data.get("stdout"),
                )
                await database.execute(query)
            print(data)
    except WebSocketDisconnect:
        pass


@app.websocket("/api/ws-activation/{activation_id}")
async def websocket_activation_endpoint(websocket: WebSocket, activation_id):
    page = f"/activation/{activation_id}"
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


@app.post("/api/rulesetfile/")
async def create_rulesetfile(rsf: RuleSetFile):
    query = rulesetfiles.insert().values(name=rsf.name, rulesets=rsf.rulesets)
    last_record_id = await database.execute(query)
    return {**rsf.dict(), "id": last_record_id}


@app.post("/api/inventory/")
async def create_inventory(i: Inventory):
    query = inventories.insert().values(name=i.name, inventory=i.inventory)
    last_record_id = await database.execute(query)
    return {**i.dict(), "id": last_record_id}


@app.post("/api/extravars/")
async def create_extravars(e: Extravars):
    query = extravars.insert().values(name=e.name, extravars=e.extravars)
    last_record_id = await database.execute(query)
    return {**e.dict(), "id": last_record_id}


@app.post("/api/activation/")
async def create_activation(a: Activation):
    query = rulesetfiles.select().where(rulesetfiles.c.id == a.rulesetfile_id)
    r = await database.fetch_one(query)
    query = inventories.select().where(inventories.c.id == a.inventory_id)
    i = await database.fetch_one(query)
    query = extravars.select().where(extravars.c.id == a.extravars_id)
    e = await database.fetch_one(query)
    query = activations.insert().values(
        name=a.name,
        rulesetfile_id=a.rulesetfile_id,
        inventory_id=a.inventory_id,
        extravars_id=a.extravars_id,
    )
    last_record_id = await database.execute(query)
    cmd, proc = await activate_rulesets(
        last_record_id,
        "quay.io/bthomass/ansible-events:latest",
        r.rulesets,
        i.inventory,
        e.extravars,
    )

    task1 = asyncio.create_task(
        read_output(proc, last_record_id), name=f"read_output {proc.pid}"
    )
    taskmanager.tasks.append(task1)

    return {**a.dict(), "id": last_record_id}

@app.post("/api/deactivate/")
async def deactivate(activation_id: int):
    await inactivate_rulesets(activation_id)
    return 


async def read_output(proc, activation_id):
    line_number = 0
    done = False
    while not done:
        line = await proc.stdout.readline()
        if len(line) == 0:
            break
        line = line.decode()
        print(f"{line}", end="")
        query = activation_logs.insert().values(
            line_number=line_number,
            log=line,
            activation_id=activation_id,
        )
        await database.execute(query)
        line_number += 1
        await connnectionmanager.broadcast(json.dumps(["Stdout", dict(stdout=line)]))


@app.get("/api/activation_logs/", response_model=List[ActivationLog])
async def read_activation_logs(activation_id: int):
    q = activation_logs.select().where(activation_logs.c.activation_id == activation_id)
    return await database.fetch_all(q)


@app.get("/api/tasks/")
async def read_tasks():
    tasks = [
        dict(name=task.get_name(), done=task.done(), cancelled=task.cancelled())
        for task in taskmanager.tasks
    ]
    return tasks


@app.post("/api/project/")
async def create_project(p: Project):
    found_hash, tempdir = await clone_project(p.url, p.git_hash)
    p.git_hash = found_hash
    query = projects.insert().values(url=p.url, git_hash=p.git_hash)
    last_record_id = await database.execute(query)
    await sync_project(last_record_id, tempdir)
    return {**p.dict(), "id": last_record_id}


@app.get("/api/project/{project_id}")
async def read_project(project_id: int):
    query = projects.select().where(projects.c.id == project_id)
    result = dict(await database.fetch_one(query))
    result["rulesets"] = await database.fetch_all(
        select(rulesetfiles.c.id, rulesetfiles.c.name)
        .select_from(projects.join(projectrules).join(rulesetfiles))
        .where(projects.c.id == project_id)
    )
    result["inventories"] = await database.fetch_all(
        select(inventories.c.id, inventories.c.name)
        .select_from(projects.join(projectinventories).join(inventories))
        .where(projects.c.id == project_id)
    )
    result["vars"] = await database.fetch_all(
        select(extravars.c.id, extravars.c.name)
        .select_from(projects.join(projectvars).join(extravars))
        .where(projects.c.id == project_id)
    )
    result["playbooks"] = await database.fetch_all(
        select(playbooks.c.id, playbooks.c.name)
        .select_from(projects.join(projectplaybooks).join(playbooks))
        .where(projects.c.id == project_id)
    )
    print(result)
    return result


@app.get("/api/projects/")
async def read_projects():
    query = projects.select()
    return await database.fetch_all(query)


@app.get("/api/playbooks/")
async def read_playbooks():
    query = playbooks.select()
    return await database.fetch_all(query)


@app.get("/api/playbook/{playbook_id}")
async def read_playbook(playbook_id: int):
    query = playbooks.select().where(playbooks.c.id == playbook_id)
    return await database.fetch_one(query)


@app.get("/api/inventories/")
async def read_inventories():
    query = inventories.select()
    return await database.fetch_all(query)


@app.get("/api/inventory/{inventory_id}")
async def read_inventory(inventory_id: int):
    query = inventories.select().where(inventories.c.id == inventory_id)
    return await database.fetch_one(query)


@app.get("/api/rulesetfiles/")
async def read_rulesetfiles():
    query = rulesetfiles.select()
    return await database.fetch_all(query)


@app.get("/api/rulesetfile/{rulesetfile_id}")
async def read_rulesetfile(rulesetfile_id: int):
    query = rulesetfiles.select().where(rulesetfiles.c.id == rulesetfile_id)
    return await database.fetch_one(query)


@app.get("/api/rulesetfile_json/{rulesetfile_id}")
async def read_rulesetfile_json(rulesetfile_id: int):
    query = rulesetfiles.select().where(rulesetfiles.c.id == rulesetfile_id)
    result = dict(await database.fetch_one(query))
    result["rulesets"] = yaml.safe_load(result["rulesets"])
    return result


@app.get("/api/extravars/")
async def read_extravars():
    query = extravars.select()
    return await database.fetch_all(query)


@app.get("/api/extravar/{extravar_id}")
async def read_extrvar(extravar_id: int):
    query = extravars.select().where(extravars.c.id == extravar_id)
    return await database.fetch_one(query)


@app.get("/api/activations/")
async def read_activations():
    query = activations.select()
    return await database.fetch_all(query)


@app.get("/api/activation/{activation_id}")
async def read_activation(activation_id: int):
    query = (
        select(
            activations.c.id,
            activations.c.name,
            rulesetfiles.c.id.label("ruleset_id"),
            rulesetfiles.c.name.label("ruleset_name"),
            inventories.c.id.label("inventory_id"),
            inventories.c.name.label("inventory_name"),
            extravars.c.id.label("extravars_id"),
            extravars.c.name.label("extravars_name"),
        )
        .select_from(activations.join(rulesetfiles).join(inventories).join(extravars))
        .where(activations.c.id == activation_id)
    )
    result = dict(await database.fetch_one(query))
    print(dict(result))
    return result


@app.get("/api/jobs/")
async def read_jobs():
    query = jobs.select()
    return await database.fetch_all(query)


@app.get("/api/job/{job_id}")
async def read_job(job_id: int):
    query = jobs.select().where(jobs.c.id == job_id)
    return await database.fetch_one(query)


@app.get("/api/job_events/{job_id}")
async def read_job_events(job_id: int):
    query1 = jobs.select().where(jobs.c.id == job_id)
    job = await database.fetch_one(query1)
    query2 = job_events.select().where(job_events.c.job_uuid == job.uuid)
    return await database.fetch_all(query2)


@app.get("/api/activation_jobs/{activation_id}")
async def read_activation_jobs(activation_id: int):
    query1 = activationjobs.select(activationjobs.c.activation_id == activation_id)
    return await database.fetch_all(query1)


# FastAPI Users


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/api/auth/jwt", tags=["auth"]
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
