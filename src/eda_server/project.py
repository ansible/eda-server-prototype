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
from asyncpg_lostream.lostream import CHUNK_SIZE, PGLargeObject
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.types import InventorySource

from .db import models
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
        project_files = find_project_files(repo_dir)
        await import_project_files(db, project_files, project.id)
        await tar_project(db, project.large_data_id, repo_dir)

        return project


async def clone_project(url: str, dest: str):
    await git_clone(url, dest)
    return await git_get_current_commit(dest)


def find_project_files(project_dir: str):
    project_files = {
        "rulebook": [],
        "inventory": [],
        "extra_var": [],
        "playbook": [],
    }

    for directory, filename in yield_files(project_dir):
        full_path = os.path.join(directory, filename)
        if is_rules_file(full_path):
            project_files["rulebook"].append((directory, filename))
        elif is_inventory_file(full_path):
            project_files["inventory"].append((directory, filename))
        elif is_extra_vars_file(full_path):
            project_files["extra_var"].append((directory, filename))
        elif is_playbook_file(full_path):
            project_files["playbook"].append((directory, filename))

    return project_files


async def import_project_files(db: AsyncSession, project_files, project_id):
    for file_type, files in project_files.items():
        for file in files:
            await import_project_file(db, file, file_type, project_id)


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


async def import_project_file(db: AsyncSession, file, file_type, project_id):
    directory, filename = file
    full_path = os.path.join(directory, filename)
    with open(full_path) as f:
        file_content = f.read()

    if file_type == "rulebook":
        await import_rulebook(db, filename, file_content, project_id)

    elif file_type == "inventory":
        await import_inventory(db, filename, file_content, project_id)

    elif file_type == "extra_var":
        await import_extra_var(db, filename, file_content, project_id)

    elif file_type == "playbook":
        await import_playbook(db, filename, file_content, project_id)


async def update_project_file(
    db: AsyncSession, file, file_type, existing_files
):
    directory, filename = file
    full_path = os.path.join(directory, filename)
    existing_file_id = next(
        file["id"] for file in existing_files if file["name"] == filename
    )
    existing_file_content = next(
        file[2] for file in existing_files if file["id"] == existing_file_id
    )

    with open(full_path) as f:
        file_content = f.read()

    if file_content != existing_file_content:
        if file_type == "rulebook":
            await update_rulebook(db, file_content, existing_file_id)

        elif file_type == "inventory":
            await update_inventory(db, file_content, existing_file_id)

        elif file_type == "extra_var":
            await update_extra_var(db, file_content, existing_file_id)

        elif file_type == "playbook":
            await update_playbook(db, file_content, existing_file_id)


async def import_rulebook(
    db: AsyncSession, filename, file_content, project_id
):
    (rulebook_id,) = (
        await db.execute(
            sa.insert(models.rulebooks).values(
                name=filename,
                rulesets=file_content,
                project_id=project_id,
            )
        )
    ).inserted_primary_key

    rulebook_data = yaml.safe_load(file_content)
    await insert_rulebook_related_data(db, rulebook_id, rulebook_data)


async def update_rulebook(db: AsyncSession, file_content, rulebook_id):
    await db.execute(
        sa.update(models.rulebooks)
        .where(models.rulebooks.c.id == rulebook_id)
        .values(rulesets=file_content)
    )

    # TODO: (doston) need to implement updating rulebook related data


async def import_inventory(
    db: AsyncSession, filename, file_content, project_id
):
    await db.execute(
        sa.insert(models.inventories).values(
            name=filename,
            inventory=file_content,
            project_id=project_id,
            inventory_source=InventorySource.PROJECT,
        )
    )


async def update_inventory(db: AsyncSession, file_content, inventory_id):
    await db.execute(
        sa.update(models.inventories)
        .where(models.inventories.c.id == inventory_id)
        .values(
            inventory=file_content,
        )
    )


async def import_extra_var(
    db: AsyncSession, filename, file_content, project_id
):
    await db.execute(
        sa.insert(models.extra_vars).values(
            name=filename,
            extra_var=file_content,
            project_id=project_id,
        )
    )


async def update_extra_var(db: AsyncSession, file_content, extra_var_id):
    await db.execute(
        sa.update(models.extra_vars)
        .where(models.extra_vars.c.id == extra_var_id)
        .values(
            extra_var=file_content,
        )
    )


async def import_playbook(
    db: AsyncSession, filename, file_content, project_id
):
    await db.execute(
        sa.insert(models.playbooks).values(
            name=filename,
            playbook=file_content,
            project_id=project_id,
        )
    )


async def update_playbook(db: AsyncSession, file_content, playbook_id):
    await db.execute(
        sa.update(models.playbooks)
        .where(models.playbooks.c.id == playbook_id)
        .values(
            playbook=file_content,
        )
    )


async def sync_existing_project(db: AsyncSession, project):
    with tempfile.TemporaryDirectory(prefix="eda-sync-project") as repo_dir:
        commit_id = await clone_project(project.url, repo_dir)
        if commit_id != project.git_hash:
            await sync_new_project_files(db, project.id, repo_dir)
            await db.execute(
                sa.update(models.projects)
                .where(models.projects.c.id == project.id)
                .values(git_hash=commit_id)
            )


async def sync_new_project_files(db: AsyncSession, project_id, repo_dir):
    new_project_files = find_project_files(repo_dir)
    existing_project_files = await retrieve_existing_project_files(
        db, project_id
    )

    for file_type, new_files in new_project_files.items():
        for new_file in new_files:
            _, filename = new_file
            existing_files = existing_project_files[file_type]
            existing_files_names = [file["name"] for file in existing_files]

            # if a file content has changed
            if filename in existing_files_names:
                await update_project_file(
                    db, new_file, file_type, existing_files
                )
            # if a file is new
            else:
                logger.info("import project file\n")
                await import_project_file(db, new_file, file_type, project_id)


async def retrieve_existing_project_files(db: AsyncSession, project_id):
    project_files = {}

    project_files["rulebook"] = (
        await db.execute(
            sa.select(
                models.rulebooks.c.id,
                models.rulebooks.c.name,
                models.rulebooks.c.rulesets,
            )
            .select_from(models.rulebooks)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    project_files["inventory"] = (
        await db.execute(
            sa.select(
                models.inventories.c.id,
                models.inventories.c.name,
                models.inventories.c.inventory,
            )
            .select_from(models.inventories)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    project_files["extra_var"] = (
        await db.execute(
            sa.select(
                models.extra_vars.c.id,
                models.extra_vars.c.name,
                models.extra_vars.c.extra_var,
            )
            .select_from(models.extra_vars)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    project_files["playbook"] = (
        await db.execute(
            sa.select(
                models.playbooks.c.id,
                models.playbooks.c.name,
                models.playbooks.c.playbook,
            )
            .select_from(models.playbooks)
            .join(models.projects)
            .where(models.projects.c.id == project_id)
        )
    ).all()

    return project_files
