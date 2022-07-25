"""
Ruleset manager

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

import asyncio
import os
import shutil
import tempfile

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db.models import playbooks

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
    Call ansible-events with ruleset, inventory, and extravars
    added as volumes to a container.
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
    print(ansible_events)
    print(cmd)

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
