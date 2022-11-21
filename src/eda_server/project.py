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

import asyncio
import logging
import os
import shutil
import tempfile

import sqlalchemy as sa
import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.types import InventorySource

from .db import models
from .db.models import extra_vars, inventories, playbooks, rulebooks
from .db.utils.lostream import CHUNK_SIZE, PGLargeObject
from .schema import ProjectCreate
from .utils import subprocess as subprocess_utils

logger = logging.getLogger("eda_server")

GIT_BIN = shutil.which("git")
TAR_BIN = shutil.which("tar")

GIT_CLONE_TIMEOUT = 30
GIT_TIMEOUT = 10
GIT_ENVIRON = {
    "GIT_TERMINAL_PROMPT": "0",
}


class GitCommandFailed(Exception):
    pass


async def run_git_command(*cmd, **kwargs):
    try:
        result = await subprocess_utils.run(
            *cmd,
            check=True,
            encoding="utf-8",
            env=GIT_ENVIRON,
            **kwargs,
        )
    except subprocess_utils.TimeoutExpired as exc:
        logging.warning("%s", str(exc))
        raise GitCommandFailed("timeout")
    except subprocess_utils.CalledProcessError as exc:
        message = (
            f"Command returned non-zero exit status {exc.returncode}:"
            f"\n\tcommand: {exc.cmd}"
            f"\n\tstderr: {exc.stderr}"
        )
        logging.warning("%s", message)
        raise GitCommandFailed(exc.stderr)
    return result


async def git_clone(url: str, dest: str) -> None:
    """
    Clone repository into the specified directory.

    :param url: The repository to clone from.
    :param dest: The directory to clone into.
    :raises GitError: If git returns non-zero exit code.
    """
    cmd = [GIT_BIN, "clone", "--quiet", url, dest]
    await run_git_command(
        *cmd,
        cwd=dest,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
        timeout=GIT_CLONE_TIMEOUT,
    )


async def git_get_current_commit(repo: str) -> str:
    """
    Return id of the current commit.

    :param repo: Path to the repository.
    :return: Current commit id.
    """
    cmd = [GIT_BIN, "rev-parse", "HEAD"]
    result = await run_git_command(
        *cmd,
        cwd=repo,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        timeout=GIT_TIMEOUT,
    )
    return result.stdout.strip()


async def create_project(
    db: AsyncSession, *, url: str, git_hash: str, name: str, description: str
):
    query = (
        sa.insert(models.projects)
        .values(
            url=url,
            git_hash=git_hash,
            name=name,
            description=description,
        )
        .returning(models.projects)
    )
    result = await db.execute(query)
    return result.first()


async def import_project(db: AsyncSession, data: ProjectCreate):
    with tempfile.TemporaryDirectory(prefix="eda-import-project") as repo_dir:
        commit_id = await clone_project(data.url, repo_dir)
        project = await create_project(
            db,
            url=data.url,
            git_hash=commit_id,
            name=data.name,
            description=data.description,
        )
        await sync_project(db, project.id, project.large_data_id, repo_dir)
        return project


async def clone_project(url: str, dest: str):
    await git_clone(url, dest)
    return await git_get_current_commit(dest)


async def sync_project(
    db: AsyncSession, project_id: int, large_data_id: int, repo_dir: str
):
    await find_rules(db, project_id, repo_dir)
    await find_inventory(db, project_id, repo_dir)
    await find_extra_vars(db, project_id, repo_dir)
    await find_playbook(db, project_id, repo_dir)
    await tar_project(db, large_data_id, repo_dir)


def is_rules_file(filename: str):
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


def yield_files(project_dir: str):
    for root, _dirs, files in os.walk(project_dir):
        if ".git" in root:
            continue
        for f in files:
            yield root, f


def expand_ruleset_sources(rulebook_data: dict) -> dict:
    expanded_ruleset_sources = {}
    if rulebook_data is not None:
        for ruleset_data in rulebook_data:
            xp_sources = []
            expanded_ruleset_sources[ruleset_data["name"]] = xp_sources
            for source in ruleset_data.get("sources", []):
                xp_src = {"name": "<unnamed>"}
                for src_key, src_val in source.items():
                    if src_key == "name":
                        xp_src["name"] = src_val
                    else:
                        xp_src["type"] = src_key.split(".")[-1]
                        xp_src["source"] = src_key
                        xp_src["config"] = src_val
                xp_sources.append(xp_src)

    return expanded_ruleset_sources


async def insert_rulebook_related_data(
    db: AsyncSession, rulebook_id: int, rulebook_data: dict
):
    expanded_sources = expand_ruleset_sources(rulebook_data)
    ruleset_values = [
        {
            "name": ruleset_data["name"],
            "rulebook_id": rulebook_id,
            "sources": expanded_sources.get(ruleset_data["name"]),
        }
        for ruleset_data in (rulebook_data or [])
    ]
    query = (
        sa.insert(models.rulesets)
        .returning(models.rulesets.c.id)
        .values(ruleset_values)
    )
    ruleset_ids = (await db.scalars(query)).all()

    rule_values = [
        {"name": rule["name"], "action": rule["action"], "ruleset_id": rsid}
        for rsid, rsdata in zip(ruleset_ids, rulebook_data)
        for rule in rsdata["rules"]
    ]
    query = sa.insert(models.rules).values(rule_values)
    await db.execute(query)


async def find_rules(db: AsyncSession, project_id: int, project_dir: str):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if not is_rules_file(full_path):
            continue

        with open(full_path) as f:
            rulesets = f.read()

        query = sa.insert(rulebooks).values(
            name=filename, rulesets=rulesets, project_id=project_id
        )
        (rulebook_id,) = (await db.execute(query)).inserted_primary_key
        # TODO(cutwater): Remove debugging print
        logger.debug(rulebook_id)

        rulebook_data = yaml.safe_load(rulesets)
        await insert_rulebook_related_data(db, rulebook_id, rulebook_data)


def is_inventory_file(filename: str):
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


async def find_inventory(db: AsyncSession, project_id: int, project_dir: str):
    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_inventory_file(full_path):
            with open(full_path) as f:
                inventory = f.read()

            query = sa.insert(inventories).values(
                name=filename,
                inventory=inventory,
                project_id=project_id,
                inventory_source=InventorySource.PROJECT,
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


def is_playbook_file(filename: str):
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


async def find_extra_vars(db: AsyncSession, project_id, project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_extra_vars_file(full_path):
            with open(full_path) as f:
                extra_var = f.read()

            query = sa.insert(extra_vars).values(
                name=filename, extra_var=extra_var, project_id=project_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


async def find_playbook(db: AsyncSession, project_id, project_dir):

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        # TODO(cutwater): Remove debugging print
        logger.debug(filename)
        if is_playbook_file(full_path):
            with open(full_path) as f:
                playbook = f.read()

            query = sa.insert(playbooks).values(
                name=filename, playbook=playbook, project_id=project_id
            )
            (record_id,) = (await db.execute(query)).inserted_primary_key
            # TODO(cutwater): Remove debugging print
            logger.debug(record_id)


async def tar_project(db: AsyncSession, large_data_id: int, project_dir: str):
    with tempfile.TemporaryDirectory() as tempdir:
        tarfile_name = os.path.join(tempdir, "project.tar.gz")

        cmd = [TAR_BIN, "zcvf", tarfile_name, "."]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=project_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            logger.critical(stdout.decode())
        if stderr:
            logger.critical(stderr.decode())

        logger.critical(tarfile_name)

        async with PGLargeObject(db, oid=large_data_id, mode="w") as lobject:
            with open(tarfile_name, "rb") as f:
                while data := f.read(CHUNK_SIZE):
                    await lobject.write(data)
