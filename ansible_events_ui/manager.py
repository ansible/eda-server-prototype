"""
Ruleset manager.

Activates rulesets together with an inventory and extravars.

Functions:
* activate_rulesets
    Arguments:
        - activation_id
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

from functools import partial
import concurrent.futures
import ansible_runner

import asyncio
import logging
import os
import shutil
import tempfile

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from .db.models import playbooks, job_instance_events
from .messages import JobEnd

logger = logging.getLogger("ansible_events_ui")

activated_rulesets = {}
ansible_events = shutil.which("ansible-events")


# TODO(cutwater): Move database query outside of this function
async def activate_rulesets(
    activation_id,
    execution_environment,
    rulesets,
    inventory,
    extravars,
    db: AsyncSession,
):
    """
    Spawn ansible-events.

    Call ansible-events with ruleset, inventory, and extravars added
    as volumes to a container.
    """
    tempdir = tempfile.mkdtemp(prefix="ruleset_manager")
    result = await db.execute(select(playbooks))
    for playbook in result.all():
        with open(os.path.join(tempdir, playbook.name), "w") as f:
            f.write(playbook.playbook)
    rules_file = os.path.join(tempdir, "rules.yml")
    with open(rules_file, "w") as f:
        f.write(rulesets)
    inventory_file = os.path.join(tempdir, "inventory.yml")
    with open(inventory_file, "w") as f:
        f.write(inventory)
    vars_file = os.path.join(tempdir, "vars.yml")
    with open(vars_file, "w") as f:
        f.write(extravars)

    # initial version using docker
    # mounting volumes is probably the wrong way to do this
    # it would be better to build it into the container or pass it
    # through a stream (stdin or socket)
    # cmd = f"docker run -v {rules_file}:/rules.yml -v {inventory_file}:/inventory.yml -v {vars_file}:/vars.yml -it {execution_environment} ansible-events --rules /rules.yml -i /inventory.yml --vars /vars.yml"  # noqa

    # try this with podman
    # cmd = f"podman run -v {rules_file}:/rules.yml -v {inventory_file}:/inventory.yml -v {vars_file}:/vars.yml -it {execution_environment} ansible-events --rules /rules.yml -i /inventory.yml --vars /vars.yml"  # noqa

    # for local development this is better
    cmd = [
        "--rules",
        rules_file,
        "-i",
        inventory_file,
        "--vars",
        vars_file,
        "--websocket-address",
        "ws://localhost:8080/api/ws2",
        "--id",
        str(activation_id),
    ]
    logger.debug(ansible_events)
    logger.debug(cmd)

    proc = await asyncio.create_subprocess_exec(
        ansible_events,
        *cmd,
        cwd=tempdir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    activated_rulesets[activation_id] = proc

    return cmd, proc


async def inactivate_rulesets(activation_id):

    try:
        activated_rulesets[activation_id].kill()
    except ProcessLookupError:
        pass


async def run_job(job_uuid, event_log, playbook, inventory, extravars, db: AsyncSession):
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


async def write_job_events(event_log, db: AsyncSession):

    while True:

        event = await event_log.get()

        if isinstance(event, JobEnd):
            break

        query = insert(job_instance_events).values(
            job_uuid=event.get("job_id"),
            counter=event.get("counter"),
            stdout=event.get("stdout"),
        )
        await db.execute(query)
        await db.commit()
