import asyncio
import logging
import os
import tempfile

import yaml
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .db.models import (
    extra_vars,
    inventories,
    playbooks,
    project_inventories,
    project_playbooks,
    project_rules,
    project_vars,
    rule_set_files,
)

logger = logging.getLogger("ansible_events_ui")


# FIXME(cutwater): Remove try: .. finally: pass
async def clone_project(url, git_hash=None):

    try:
        tempdir = tempfile.mkdtemp(prefix="clone_project")
        logger.debug(tempdir)

        cmd = f"git clone {url} ."

        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            logger.debug(stdout.decode())
        if stderr:
            logger.debug(stderr.decode())

        cmd = "git rev-parse HEAD"

        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=tempdir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            return stdout.decode().strip(), tempdir
        if stderr:
            return stderr.decode().strip(), tempdir

    finally:
        pass


# FIXME(cutwater): Remove try: .. finally: pass
async def sync_project(project_id, tempdir, db: AsyncSession):

    try:

        await find_rules(project_id, tempdir, db)
        await find_inventory(project_id, tempdir, db)
        await find_extra_vars(project_id, tempdir, db)
        await find_playbook(project_id, tempdir, db)

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
    except Exception:
        logger.exception(filename)
        return False

    return True


def yield_files(project_dir):

    for root, _dirs, files in os.walk(project_dir):
        if ".git" in root:
            continue
        for f in files:
            yield root, f


async def find_rules(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_rules_file(full_path):
            with open(full_path) as f:
                rulesets = f.read()

            query = insert(rule_set_files).values(
                name=filename, rulesets=rulesets
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)

            query = insert(project_rules).values(
                project_id=project_id, rule_set_file_id=record_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


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
    except Exception:
        logger.exception(filename)
        return False

    return True


async def find_inventory(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_inventory_file(full_path):
            with open(full_path) as f:
                inventory = f.read()

            query = insert(inventories).values(
                name=filename, inventory=inventory
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)

            query = insert(project_inventories).values(
                project_id=project_id, inventory_id=record_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


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
    except Exception:
        logger.exception(filename)
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


async def find_extra_vars(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_extra_vars_file(full_path):
            with open(full_path) as f:
                extra_var = f.read()

            query = insert(extra_vars).values(
                name=filename, extra_var=extra_var
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)

            query = insert(project_vars).values(
                project_id=project_id, vars_id=record_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


async def find_playbook(project_id, project_dir, db: AsyncSession):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_playbook_file(full_path):
            with open(full_path) as f:
                playbook = f.read()

            query = insert(playbooks).values(name=filename, playbook=playbook)
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)

            query = insert(project_playbooks).values(
                project_id=project_id, playbook_id=record_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)
