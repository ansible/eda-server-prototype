import tempfile
import os
import asyncio
import shutil
import yaml

from .models import (
    metadata,
    rulesets,
    inventories,
    extravars,
)

from .database import database

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

        return await sync_project(url, tempdir)

    finally:
        pass


async def sync_project(url, tempdir):

    try:

        cmd = "git rev-parse HEAD"

        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        await find_rules(tempdir)
        await find_inventory(tempdir)
        await find_extravars(tempdir)

        if stdout:
            # print(stdout.decode())
            return stdout.decode().strip()
        if stderr:
            # print(stderr.decode())
            return stderr.decode().strip()

    finally:
        pass


def is_rules_file(filename):
    if not filename.endswith('.yml'):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, list):
                return False
            for entry in data:
                if 'rules' not in entry:
                    return False
    except Exception as e:
        print(f'{filename} {e}')
        return False

    return True


def yield_files(project_dir):

    for root, dirs, files in os.walk(project_dir):
        if '.git' in root:
            continue
        for f in files:
            yield root, f



async def find_rules(project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        print(filename)
        if is_rules_file(full_path):
            with open(full_path) as f:
                rules = f.read()
            query = rulesets.insert().values(name=filename, rules=rules)
            last_record_id = await database.execute(query)
            print(last_record_id)


def is_inventory_file(filename):
    if not filename.endswith('.yml'):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, dict):
                return False
            if 'all' not in data:
                return False
    except Exception as e:
        print(f'{filename} {e}')
        return False

    return True


async def find_inventory(project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        print(filename)
        if is_inventory_file(full_path):
            with open(full_path) as f:
                inventory = f.read()
            query = inventories.insert().values(name=filename, inventory=inventory)
            last_record_id = await database.execute(query)
            print(last_record_id)


def is_playbook_file(filename):
    if not filename.endswith('.yml'):
        return False
    try:
        with open(filename) as f:
            data = yaml.safe_load(f.read())
            if not isinstance(data, list):
                return False
            for entry in data:
                if 'tasks' in data:
                    return True
                if 'roles' in data:
                    return True
    except Exception as e:
        print(f'{filename} {e}')
        return False

    return False


def is_extravars_file(filename):
    if not filename.endswith('.yml'):
        return False
    return (
        not is_rules_file(filename)
        and not is_inventory_file(filename)
        and not is_playbook_file(filename)
    )


async def find_extravars(project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        print(filename)
        if is_extravars_file(full_path):
            with open(full_path) as f:
                extravar = f.read()
            query = extravars.insert().values(name=filename, extravars=extravar)
            last_record_id = await database.execute(query)
            print(last_record_id)
