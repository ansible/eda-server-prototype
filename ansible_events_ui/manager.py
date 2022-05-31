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

activated_rulesets = dict()
activated_rulesets_seq = count(1)


async def activate_rulesets(execution_environment, rulesets, inventory, extravars):
    """
    Call ansible-events with rulset, inventory, and extravars added as volumes to a container
    """

    try:
        tempdir = tempfile.mkdtemp(prefix='ruleset_manager')
        rules_file = os.path.join(tempdir, "rules.yml")
        with open(rules_file, 'w') as f:
            f.write(rulesets)
        inventory_file = os.path.join(tempdir, "inventory.yml")
        with open(inventory_file, 'w') as f:
            f.write(inventory)
        vars_file = os.path.join(tempdir, "vars.yml")
        with open(vars_file, 'w') as f:
            f.write(extravars)

        cmd = f"docker run -v {rules_file}:/rules.yml -v {inventory_file}:/inventory.yml -v {vars_file}:/vars.yml -it {execution_environment} ansible-events --rules /rules.yml -i /inventory.yml --vars /vars.yml"

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        print(f'[{cmd!r} exited with {proc.returncode}]')
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')

        activated_rulesets[next(activated_rulesets_seq)] = proc
    finally:
        shutil.rmtree(tempdir)


async def inactivate_rulesets(rulesets_id):
    pass
