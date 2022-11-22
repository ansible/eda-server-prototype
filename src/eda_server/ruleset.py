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

"""
Ruleset manager.

Activates rulesets together with an inventory and extravars.

Functions:
* activate_rulesets
    Arguments:
        - activation_id
        - activation_instance_large_data_id
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
import aiodocker.images
import ansible_runner
from asyncpg_lostream.lostream import CHUNK_SIZE, PGLargeObject
from sqlalchemy import insert

from eda_server.managers import taskmanager

from .db.models import job_instance_events
from .managers import updatemanager
from .messages import JobEnd

logger = logging.getLogger("eda_server")

activated_rulesets = {}
ansible_rulebook = shutil.which("ansible-rulebook")
if ansible_rulebook is None:
    raise Exception("ansible-rulebook not found")
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
    large_data_id,
    execution_environment,
    rulesets,
    inventory,
    extravars,
    working_directory,
    host,
    port,
    db_factory,
):
    local_working_directory = working_directory
    ensure_directory(local_working_directory)

    logger.debug("activate_rulesets %s %s", activation_id, deployment_type)

    # TODO(ben): Change to enum
    if deployment_type == "local":

        # for local development this is better
        cmd_args = [
            ansible_rulebook,
            "--worker",
            "--websocket-address",
            "ws://localhost:8080/api/ws2",
            "--id",
            str(activation_id),
        ]
        logger.debug(ansible_rulebook)
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
            read_output(proc, activation_id, large_data_id, db_factory),
            name=f"read_output {proc.pid}",
        )
        taskmanager.tasks.append(task)

    elif deployment_type == "docker" or deployment_type == "podman":

        docker = aiodocker.Docker()

        host = "eda-server"

        try:
            await aiodocker.images.DockerImages(docker).pull(
                execution_environment
            )

            logger.debug("Creating container")
            logger.debug("Host: %s", host)
            logger.debug("Port: %s", port)
            container = await docker.containers.create(
                {
                    "Cmd": [
                        "ssh-agent",
                        "ansible-rulebook",
                        "--worker",
                        "--websocket-address",
                        f"ws://{host}:{port}/api/ws2",
                        "--id",
                        str(activation_id),
                        "--debug",
                    ],
                    "Image": execution_environment,
                    "Env": ["ANSIBLE_FORCE_COLOR=True"],
                    "ExtraHosts": ["host.docker.internal:host-gateway"],
                    "ExposedPorts": {"8000/tcp": {}},
                    "HostConfig": {
                        "PortBindings": {"8000/tcp": [{"HostPort": "8000"}]},
                        "NetworkMode": "eda-network",
                    },
                }
            )
            logger.debug("Starting container")
            await container.start()
        except aiodocker.exceptions.DockerError as e:
            logger.error("Failed to start container: %s", e)
            await container.delete()
            await docker.close()
            raise

        activated_rulesets[activation_id] = container

        task = asyncio.create_task(
            read_log(
                docker, container, activation_id, large_data_id, db_factory
            ),
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
    proc, activation_instance_id, activation_instance_large_data_id, db_factory
):

    try:
        logger.debug(
            "read_output %s %s %s",
            proc.pid,
            activation_instance_id,
            activation_instance_large_data_id,
        )
        async with db_factory() as db:
            async with PGLargeObject(
                db, oid=activation_instance_large_data_id, mode="w"
            ) as lobject:
                while True:
                    buff = await proc.stdout.read(CHUNK_SIZE)
                    if not buff:
                        break
                    buff = buff.decode()
                    logger.debug("read_output %s", buff)
                    await lobject.write(buff)
                    await db.commit()
                    await updatemanager.broadcast(
                        f"/activation_instance/{activation_instance_id}",
                        json.dumps(["Stdout", {"stdout": buff.decode()}]),
                    )

    except Exception as e:
        logger.error("read_output %s", e)
    finally:
        logger.info("read_output complete")


async def read_log(
    docker,
    container,
    activation_instance_id,
    activation_instance_large_data_id,
    db_factory,
):
    try:
        async with db_factory() as db:
            async with PGLargeObject(
                db, oid=activation_instance_large_data_id, mode="w"
            ) as lobject:
                async for chunk in container.log(
                    stdout=True, stderr=True, follow=True
                ):
                    await lobject.write(chunk.encode())
                    await db.commit()
                    await updatemanager.broadcast(
                        f"/activation_instance/{activation_instance_id}",
                        json.dumps(["Stdout", {"stdout": chunk}]),
                    )
                await docker.close()
    except Exception as e:
        logger.error("read_log %s", e)


async def run_job(
    job_uuid, event_log, playbook, inventory, extravars, db_factory
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


async def write_job_events(event_log, job_instance_id, db_factory):

    while True:

        event = await event_log.get()

        if isinstance(event, JobEnd):
            break

        if event.get("stdout"):
            await updatemanager.broadcast(
                f"/job_instance/{job_instance_id}",
                json.dumps(["Stdout", {"stdout": event.get("stdout")}]),
            )

        async with db_factory() as db:
            query = insert(job_instance_events).values(
                job_uuid=event.get("job_id"),
                counter=event.get("counter"),
                stdout=event.get("stdout"),
            )
            await db.execute(query)
            await db.commit()
