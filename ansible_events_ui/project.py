import asyncio
import os
import tempfile

import yaml

from .database import database
from .models import (
    extra_vars,
    inventories,
    playbooks,
    project_inventories,
    project_playbooks,
    project_rules,
    project_vars,
    rule_set_files,
)


async def clone_project(url, git_hash=None):

    try:
        tempdir = tempfile.mkdtemp(prefix="clone_project")
        print(tempdir)

        cmd = f"git clone {url} ."

        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            print(stdout.decode())
        if stderr:
            print(stderr.decode())

        cmd = "git rev-parse HEAD"

        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            # print(stdout.decode())
            return stdout.decode().strip(), tempdir
        if stderr:
            # print(stderr.decode())
            return stderr.decode().strip(), tempdir

    finally:
        pass


async def sync_project(project_id, tempdir):

    try:

        await find_rules(project_id, tempdir)
        await find_inventory(project_id, tempdir)
        await find_extra_vars(project_id, tempdir)
        await find_playbook(project_id, tempdir)

    finally:
        pass


def is_rules_file(filename):
    if not filename.endswith(".yml"):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, list):
                return False
            for entry in data:
                if "rules" not in entry:
                    return False
    except Exception as e:
        print(f"{filename} {e}")
        return False

    return True


def yield_files(project_dir):

    for root, dirs, files in os.walk(project_dir):
        if ".git" in root:
            continue
        for f in files:
            yield root, f


async def find_rules(project_id, project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        print(filename)
        if is_rules_file(full_path):
            with open(full_path) as f:
                rulesets = f.read()
            query = rule_set_files.insert().values(
                name=filename, rulesets=rulesets
            )
            last_record_id = await database.execute(query)
            print(last_record_id)
            query = project_rules.insert().values(
                project_id=project_id, rule_set_file_id=last_record_id
            )
            last_record_id = await database.execute(query)
            print(last_record_id)


def is_inventory_file(filename):
    if not filename.endswith(".yml"):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, dict):
                return False
            if "all" not in data:
                return False
    except Exception as e:
        print(f"{filename} {e}")
        return False

    return True


async def find_inventory(project_id, project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        print(filename)
        if is_inventory_file(full_path):
            with open(full_path) as f:
                inventory = f.read()
            query = inventories.insert().values(
                name=filename, inventory=inventory
            )
            last_record_id = await database.execute(query)
            print(last_record_id)
            query = project_inventories.insert().values(
                project_id=project_id, inventory_id=last_record_id
            )
            last_record_id = await database.execute(query)
            print(last_record_id)


def is_playbook_file(filename):
    if not filename.endswith(".yml"):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, list):
                return False
            for entry in data:
                if "tasks" in entry:
                    return True
                if "roles" in entry:
                    return True
    except Exception as e:
        print(f"{filename} {e}")
        return False
    return False


def is_extra_vars_file(filename):
    if not filename.endswith(".yml"):
        return False
    return (
        not is_rules_file(filename)
        and not is_inventory_file(filename)
        and not is_playbook_file(filename)
    )


async def find_extra_vars(project_id, project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        print(filename)
        if is_extra_vars_file(full_path):
            with open(full_path) as f:
                extra_var = f.read()
            query = extra_vars.insert().values(
                name=filename, extra_var=extra_var
            )
            last_record_id = await database.execute(query)
            print(last_record_id)
            query = project_vars.insert().values(
                project_id=project_id, vars_id=last_record_id
            )
            last_record_id = await database.execute(query)
            print(last_record_id)


async def find_playbook(project_id, project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        print(filename)
        if is_playbook_file(full_path):
            with open(full_path) as f:
                playbook = f.read()
            query = playbooks.insert().values(name=filename, playbook=playbook)
            last_record_id = await database.execute(query)
            print(last_record_id)
            query = project_playbooks.insert().values(
                project_id=project_id, playbook_id=last_record_id
            )
            last_record_id = await database.execute(query)
            print(last_record_id)
