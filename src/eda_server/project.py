import asyncio
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterator, Literal, Optional

import sqlalchemy as sa
import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from .db import models
from .db.models import extra_vars, inventories, playbooks, rulebooks
from .db.utils.lostream import CHUNK_SIZE, PGLargeObject
from .schema import ProjectCreate
from .utils import subprocess as subprocess_utils

logger = logging.getLogger("eda_server")

GIT_BIN = shutil.which("git")
TAR_BIN = shutil.which("tar")

DEFAULT_TIMEOUT = 10
GIT_CLONE_TIMEOUT = 30
GIT_ARCHIVE_TIMEOUT = 30
GIT_ENVIRON = {
    "GIT_TERMINAL_PROMPT": "0",
}

TEMPFILE_PREFIX = "eda-import-project"

# ---- IMPORT -----------------------------------------------------------------


async def import_project(db: AsyncSession, data: ProjectCreate):
    with tempfile.TemporaryDirectory(prefix=TEMPFILE_PREFIX) as repo_dir:
        commit_id = await clone_project(data.url, repo_dir)
        project = await create_project(
            db,
            url=data.url,
            git_hash=commit_id,
            name=data.name,
            description=data.description,
        )
        await sync_project(db, project.id, repo_dir)
        await tar_project(db, project.large_data_id, repo_dir)
        return project


# ---- GIT --------------------------------------------------------------------


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
    cmd = [GIT_BIN, "clone", "--quiet", "--depth", "1", url, dest]
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
        timeout=DEFAULT_TIMEOUT,
    )
    return result.stdout.strip()


async def git_archive(
    repo: str,
    commit_id: str,
    *,
    output: str,
    format: Literal["tar", "tar.gz"] = "tar.gz",
):
    cmd = [GIT_BIN, "archive", "--format", format, "-o", output, commit_id]
    await run_git_command(
        *cmd,
        cwd=repo,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
        timeout=GIT_ARCHIVE_TIMEOUT,
    )


async def clone_project(url: str, dest: str):
    await git_clone(url, dest)
    return await git_get_current_commit(dest)


# ---- SYNC -------------------------------------------------------------------


async def sync_project(db: AsyncSession, project_id: int, repo_dir: str):
    for result in scan_project(repo_dir):
        if result.kind is ProjectFileKind.RULEBOOK:
            rulebook_id = await create_rulebook(
                db,
                project_id=project_id,
                name=result.filename,
                rulesets=result.raw_content,
            )
            await create_rules(db, rulebook_id, result.content)
        elif result.kind is ProjectFileKind.PLAYBOOK:
            await create_playbook(
                db,
                project_id=project_id,
                name=result.filename,
                playbook=result.raw_content,
            )
        elif result.kind is ProjectFileKind.INVENTORY:
            await create_inventory(
                db,
                project_id=project_id,
                name=result.filename,
                inventory=result.raw_content,
            )
        elif result.kind is ProjectFileKind.EXTRA_VARS:
            await create_extra_var(
                db,
                project_id=project_id,
                name=result.filename,
                extra_var=result.raw_content,
            )


IGNORED_DIRS = frozenset([".git", ".github"])


class ProjectFileKind(Enum):
    RULEBOOK = "rulebook"
    INVENTORY = "inventory"
    EXTRA_VARS = "extra_vars"
    PLAYBOOK = "playbook"


@dataclass
class ScanResult:
    kind: ProjectFileKind
    filename: str
    raw_content: str
    content: Any


def get_file_kind(content: Any) -> ProjectFileKind:
    if is_rulebook_file(content):
        return ProjectFileKind.RULEBOOK
    elif is_inventory_file(content):
        return ProjectFileKind.INVENTORY
    elif is_playbook_file(content):
        return ProjectFileKind.PLAYBOOK
    else:
        return ProjectFileKind.EXTRA_VARS


def scan_file(path: str) -> Optional[ScanResult]:
    _, ext = os.path.splitext(path)
    if ext not in (".yml", ".yaml"):
        return None

    try:
        with open(path) as f:
            raw_content = f.read()
    except OSError as exc:
        logger.warning("Cannot open file %s: %s", os.path.basename(path), exc)
        return None

    try:
        content = yaml.safe_load(raw_content)
    except yaml.YAMLError as exc:
        logger.warning("Invalid YAML file %s: %s", os.path.basename(path), exc)
        return None

    kind = get_file_kind(content)
    if kind is None:
        return None

    return ScanResult(
        kind=kind,
        filename=os.path.basename(path),
        raw_content=raw_content,
        content=content,
    )


def scan_project(project_dir: str) -> Iterator[ScanResult]:
    for root, dirs, files in os.walk(project_dir):
        # Skip ignored directories
        dirs[:] = [x for x in dirs if x not in IGNORED_DIRS]
        for filename in files:
            path = os.path.join(root, filename)
            try:
                result = scan_file(path)
            except Exception:
                logger.exception(
                    "Unexpected exception when scanning file %s", path
                )
                continue
            if result is not None:
                yield result


def is_rulebook_file(data: Any):
    if not isinstance(data, list):
        return False
    return all("rules" in entry for entry in data)


def is_playbook_file(data: Any):
    if not isinstance(data, list):
        return False
    for entry in data:
        if not isinstance(entry, dict):
            return False
        if entry.keys() & {"tasks", "roles"}:
            return True
    return False


def is_inventory_file(data: Any):
    if not isinstance(data, dict):
        return False
    return "all" in data


# ---- DATABASE ---------------------------------------------------------------


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


# TODO(cutwater): Move into the Table Data Gateway pattern implementation.
async def create_rules(
    db: AsyncSession, rulebook_id: int, rulebook_data: dict
):
    ruleset_values = [
        {"name": ruleset_data["name"], "rulebook_id": rulebook_id}
        for ruleset_data in rulebook_data
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


async def create_rulebook(
    db: AsyncSession, *, project_id: int, name: str, rulesets: str
):
    query = sa.insert(rulebooks).values(
        name=name, rulesets=rulesets, project_id=project_id
    )
    (id_,) = (await db.execute(query)).inserted_primary_key
    return id_


async def create_inventory(
    db: AsyncSession, *, project_id: int, name: str, inventory: str
):
    query = sa.insert(inventories).values(
        name=name, inventory=inventory, project_id=project_id
    )
    (id_,) = (await db.execute(query)).inserted_primary_key
    return id_


async def create_extra_var(
    db: AsyncSession, *, project_id: int, name: str, extra_var: str
):
    query = sa.insert(extra_vars).values(
        name=name, extra_var=extra_var, project_id=project_id
    )
    (id_,) = (await db.execute(query)).inserted_primary_key
    return id_


async def create_playbook(
    db: AsyncSession, *, project_id: int, name: str, playbook: str
):
    query = sa.insert(playbooks).values(
        name=name, playbook=playbook, project_id=project_id
    )
    (id_,) = (await db.execute(query)).inserted_primary_key
    return id_


# ---- ARCHIVE ----------------------------------------------------------------


async def tar_project(db: AsyncSession, large_data_id: int, project_dir: str):
    archive_path = os.path.join(project_dir, "project.tar.gz")

    await git_archive(project_dir, "HEAD", output=archive_path)

    async with PGLargeObject(db, oid=large_data_id, mode="w") as lobject:
        with open(archive_path, "rb") as f:
            while data := f.read(CHUNK_SIZE):
                await lobject.write(data)
