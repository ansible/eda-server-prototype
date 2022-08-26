import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models

TEST_EXTRA_VAR = """
---
collections:
  - community.general
  - benthomasson.eda  # 1.3.0
"""

TEST_INVENTORY = """
---
all:
    hosts:
        localhost:
            ansible_connection: local
            ansible_python_interpreter: /usr/bin/python3
"""

TEST_RULEBOOK = """
---
- name: hello
  hosts: localhost
  gather_facts: false
  tasks:
    - debug:
        msg: hello
"""

TEST_PLAYBOOK = TEST_RULEBOOK


@pytest.mark.asyncio
async def test_create_delete_project(client: AsyncClient, db: AsyncSession):
    query = sa.insert(models.projects).values(
        url="https://github.com/benthomasson/eda-project"
    )
    await db.execute(query)

    query = sa.insert(models.extra_vars).values(
        name="vars.yml",
        extra_var=TEST_EXTRA_VAR,
        project_id=1,
    )
    await db.execute(query)

    query = sa.insert(models.inventories).values(
        name="inventory.yml",
        inventory=TEST_INVENTORY,
        project_id=1,
    )
    await db.execute(query)

    query = sa.insert(models.rulebooks).values(
        name="ruleset.yml",
        rulesets=TEST_RULEBOOK,
        project_id=1,
    )
    await db.execute(query)

    query = sa.insert(models.playbooks).values(
        name="hello.yml",
        playbook=TEST_PLAYBOOK,
        project_id=1,
    )
    await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1

    extra_vars = (await db.execute(sa.select(models.extra_vars))).all()
    assert len(extra_vars) == 1

    inventories = (await db.execute(sa.select(models.inventories))).all()
    assert len(inventories) == 1

    rulebooks = (await db.execute(sa.select(models.rulebooks))).all()
    assert len(rulebooks) == 1

    playbooks = (await db.execute(sa.select(models.playbooks))).all()
    assert len(playbooks) == 1

    response = await client.delete("/api/project/1")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 0

    extra_vars = (await db.execute(sa.select(models.extra_vars))).all()
    assert len(extra_vars) == 0

    inventories = (await db.execute(sa.select(models.inventories))).all()
    assert len(inventories) == 0

    rulebooks = (await db.execute(sa.select(models.rulebooks))).all()
    assert len(rulebooks) == 0

    playbooks = (await db.execute(sa.select(models.playbooks))).all()
    assert len(playbooks) == 0


@pytest.mark.asyncio
async def test_delete_project_not_found(client: AsyncClient):
    response = await client.delete("/api/project/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
