'''

Ruleset manager

Activates rulesets together with an inventory and extravars.

Functions:
* activate_rulesets
    Arguments:
        - rulesets:
        - inventory:
        - extravars:
    Returns a rulesets id
* inactivate_ruleset
    Arguments:
        - rulesets_id
    Returns None
'''

import tempfile
import os
import asyncio
import shutil

from itertools import count

from .models import playbooks
from .database import database

activated_rulesets = dict()
activated_rulesets_seq = count(1)


async def activate_rulesets(activation_id, execution_environment, rulesets, inventory, extravars):
    """
    Call ansible-events with rulset, inventory, and extravars added as volumes to a container
    """

    try:
        tempdir = tempfile.mkdtemp(prefix='ruleset_manager')
        query = playbooks.select()
        for playbook in await database.fetch_all(query):
            with open(os.path.join(tempdir, playbook.name), 'w') as f:
                f.write(playbook.playbook)
        rules_file = os.path.join(tempdir, "rules.yml")
        with open(rules_file, 'w') as f:
            f.write(rulesets)
        inventory_file = os.path.join(tempdir, "inventory.yml")
        with open(inventory_file, 'w') as f:
            f.write(inventory)
        vars_file = os.path.join(tempdir, "vars.yml")
        with open(vars_file, 'w') as f:
            f.write(extravars)

        # initial version using docker
        # mounting volumes is probably the wrong way to do this
        # it would be better to build it into the container or pass it through a stream (stdin or socket)
        #cmd = f"docker run -v {rules_file}:/rules.yml -v {inventory_file}:/inventory.yml -v {vars_file}:/vars.yml -it {execution_environment} ansible-events --rules /rules.yml -i /inventory.yml --vars /vars.yml"

        # try this with podman
        #cmd = f"podman run -v {rules_file}:/rules.yml -v {inventory_file}:/inventory.yml -v {vars_file}:/vars.yml -it {execution_environment} ansible-events --rules /rules.yml -i /inventory.yml --vars /vars.yml"

        # for local development this is better
        cmd = f"ansible-events --rules {rules_file} -i {inventory_file} --vars {vars_file} --websocket-address ws://localhost:8080/api/ws2 --id {activation_id}"
        print(cmd)

        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT)


        activated_rulesets[next(activated_rulesets_seq)] = proc

        return cmd, proc
    finally:
        pass


async def inactivate_rulesets(rulesets_id):
    pass
