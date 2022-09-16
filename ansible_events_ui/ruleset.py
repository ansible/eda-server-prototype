"""
Ruleset manager.

Activates rulesets together with an inventory and extravars.

Functions:
* activate_rulesets
    Arguments:
        - activation_id
        - activation_instance_log_id
        - execution_environment
        - rulesets
        - inventory
        - extravars
    Returns a tuple of the command run and the process
* inactivate_ruleset
    Arguments:
        - activation_id
    Returns None
"""

import asyncio
import concurrent.futures
import json
import logging
import os
import shutil
import tempfile
from functools import partial

import aiodocker
import ansible_runner
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db.utils.lostream import CHUNK_SIZE, PGLargeObject
from ansible_events_ui.managers import taskmanager

from .db.models import job_instance_events
from .managers import updatemanager
from .messages import JobEnd

logger = logging.getLogger("ansible_events_ui")

activated_rulesets = {}
ansible_events = shutil.which("ansible-events")
if ansible_events is None:
    raise Exception("ansible-events not found")
ssh_agent = shutil.which("ssh-agent")
if ssh_agent is None:
    raise Exception("ssh-agent not found")


def ensure_directory(directory):
    if os.path.exists(directory):
        return directory
    else:
        os.makedirs(directory)
        return directory


# TODO(cutwater): Move database query outside of this function
async def activate_rulesets(
    deployment_type,
    activation_id,
    log_id,
    execution_environment,
    rulesets,
    inventory,
    extravars,
    working_directory,
    host,
    port,
    db: AsyncSession,
    encoding,
):
    """
    Spawn ansible-events.

    Call ansible-events with ruleset, inventory, and extravars added
    as volumes to a container.
    """
    local_working_directory = working_directory
    ensure_directory(local_working_directory)

    # TODO(ben): Change to enum
    if deployment_type == "local":

        # for local development this is better
        cmd_args = [
            ansible_events,
            "--worker",
            "--websocket-address",
            "ws://localhost:8080/api/ws2",
            "--id",
            str(activation_id),
        ]
        logger.debug(ansible_events)
        logger.debug(cmd_args)

        proc = await asyncio.create_subprocess_exec(
            ssh_agent,
            *cmd_args,
            cwd=local_working_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        activated_rulesets[activation_id] = proc

        task = asyncio.create_task(
            read_output(proc, activation_id, log_id, db, encoding),
            name=f"read_output {proc.pid}",
        )
        taskmanager.tasks.append(task)

    elif deployment_type == "docker" or deployment_type == "podman":

        docker = aiodocker.Docker()

        if deployment_type == "docker":
            host = "host.docker.internal"

        container = await docker.containers.create(
            {
                "Cmd": [
                    "ssh-agent",
                    "ansible-events",
                    "--worker",
                    "--websocket-address",
                    f"ws://{host}:{port}/api/ws2",
                    "--id",
                    str(activation_id),
                ],
                "Image": execution_environment,
                "Env": ["ANSIBLE_FORCE_COLOR=True"],
                "ExtraHosts": ["host.docker.internal:host-gateway"],
            }
        )
        try:
            await container.start()
        except aiodocker.exceptions.DockerError as e:
            logger.error("Failed to start container: %s", e)
            await container.delete()
            raise

        activated_rulesets[activation_id] = container

        task = asyncio.create_task(
            read_log(docker, container, activation_id, log_id, db, encoding),
            name=f"read_log {container}",
        )
        taskmanager.tasks.append(task)

    elif deployment_type == "k8s":
        # Calls to the k8s apis.
        logger.error("k8s deployment not implemented yet")
    else:
        raise Exception("Unsupported deployment_type")


async def inactivate_rulesets(activation_id):
    try:
        activated_rulesets[activation_id].kill()
    except ProcessLookupError:
        pass


async def read_output(
    proc, activation_instance_id, activation_instance_log_id, db, encoding
):
    # TODO(cutwater): Replace with FastAPI dependency injections,
    #   that is available in BackgroundTasks
    async with PGLargeObject(
        db, oid=activation_instance_log_id, mode="wb", encoding=encoding
    ) as lobject:
        for buff in iter(lambda: proc.stdout.read(CHUNK_SIZE), b""):
            await lobject.write(buff)
            await db.commit()
            await updatemanager.broadcast(
                f"/activation_instance/{activation_instance_id}",
                json.dumps(["Stdout", {"stdout": buff.decode()}]),
            )


async def read_log(
    docker,
    container,
    activation_instance_id,
    activation_instance_log_id,
    db,
    encoding,
):
    async with PGLargeObject(
        db, oid=activation_instance_log_id, mode="wt", encoding=encoding
    ) as lobject:
        async for chunk in container.log(
            stdout=True, stderr=True, follow=True
        ):
            await lobject.write(chunk)
            await db.commit()
            await updatemanager.broadcast(
                f"/activation_instance/{activation_instance_id}",
                json.dumps(["Stdout", {"stdout": chunk}]),
            )
        await docker.close()


async def run_job(
    job_uuid, event_log, playbook, inventory, extravars, db: AsyncSession
):
    loop = asyncio.get_running_loop()
    task_pool = concurrent.futures.ThreadPoolExecutor()

    host_limit = "localhost"
    verbosity = 0
    json_mode = False

    def event_callback(event, *args, **kwargs):
        event["job_id"] = job_uuid
        event_log.put_nowait(event)

    temp = tempfile.mkdtemp(prefix="run_playbook")

    os.mkdir(os.path.join(temp, "env"))
    with open(os.path.join(temp, "env", "extravars"), "w") as f:
        f.write(extravars)
    os.mkdir(os.path.join(temp, "inventory"))
    with open(os.path.join(temp, "inventory", "hosts"), "w") as f:
        f.write(inventory)
    os.mkdir(os.path.join(temp, "project"))
    with open(os.path.join(temp, "project", "playbook.yml"), "w") as f:
        f.write(playbook)

    await loop.run_in_executor(
        task_pool,
        partial(
            ansible_runner.run,
            playbook="playbook.yml",
            private_data_dir=temp,
            limit=host_limit,
            verbosity=verbosity,
            event_handler=event_callback,
            json_mode=json_mode,
        ),
    )

    await event_log.put(JobEnd(job_uuid))


async def write_job_events(event_log, db: AsyncSession, job_instance_id):

    while True:

        event = await event_log.get()

        if isinstance(event, JobEnd):
            break

        if event.get("stdout"):
            await updatemanager.broadcast(
                f"/job_instance/{job_instance_id}",
                json.dumps(["Stdout", {"stdout": event.get("stdout")}]),
            )

        query = insert(job_instance_events).values(
            job_uuid=event.get("job_id"),
            counter=event.get("counter"),
            stdout=event.get("stdout"),
        )
        await db.execute(query)
        await db.commit()
