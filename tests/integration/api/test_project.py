import hashlib
from unittest import mock

import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models

TEST_PROJECT = {
    "url": "https://git.example.com/sample/test-project",
    "name": "Test Name",
    "description": "This is a test description",
}

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
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )
    result = await db.execute(query)

    (inserted_project_id,) = result.inserted_primary_key

    query = sa.insert(models.extra_vars).values(
        name="vars.yml",
        extra_var=TEST_EXTRA_VAR,
        project_id=inserted_project_id,
    )
    await db.execute(query)

    query = sa.insert(models.inventories).values(
        name="inventory.yml",
        inventory=TEST_INVENTORY,
        project_id=inserted_project_id,
    )
    await db.execute(query)

    query = sa.insert(models.rulebooks).values(
        name="ruleset.yml",
        rulesets=TEST_RULEBOOK,
        project_id=inserted_project_id,
    )
    await db.execute(query)

    query = sa.insert(models.playbooks).values(
        name="hello.yml",
        playbook=TEST_PLAYBOOK,
        project_id=inserted_project_id,
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

    response = await client.delete(f"/api/project/{projects[0].id}")
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


@pytest.mark.asyncio
@mock.patch("ansible_events_ui.api.project.clone_project")
@mock.patch("ansible_events_ui.api.project.sync_project")
async def test_create_project(
    sync_project: mock.Mock,
    clone_project: mock.Mock,
    client: AsyncClient,
    db: AsyncSession,
):
    found_hash = hashlib.sha1(b"test").hexdigest()
    clone_project.return_value = found_hash, "/tmp/test-create-project"

    response = await client.post(
        "/api/projects/",
        json=TEST_PROJECT,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == TEST_PROJECT["name"]

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]
    assert project["id"] == data["id"]
    assert project["name"] == TEST_PROJECT["name"]
    assert project["url"] == TEST_PROJECT["url"]

    clone_project.assert_called_once_with(TEST_PROJECT["url"], None)
    sync_project.assert_called_once_with(
        project["id"], "/tmp/test-create-project", db
    )


@pytest.mark.asyncio
async def test_create_project_bad_entity(
    client: AsyncClient, db: AsyncSession
):
    bad_project = {
        "url": None,
        "name": "Test Name",
        "description": "This is a test description",
    }
    response = await client.post(
        "/api/projects/",
        json=bad_project,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, db: AsyncSession):

    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )

    await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]

    response = await client.get(f"/api/projects/{project['id']}")

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert data["name"] == TEST_PROJECT["name"]
    assert data["url"] == TEST_PROJECT["url"]


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient, db: AsyncSession):

    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )

    await db.execute(query)

    response = await client.get("/api/projects/100")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_edit_project(client: AsyncClient, db: AsyncSession):

    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )

    await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]

    response = await client.patch(
        f"/api/projects/{project['id']}",
        json={"name": "new test name"},
    )

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert data["name"] == "new test name"
    assert data["url"] == TEST_PROJECT["url"]


@pytest.mark.asyncio
async def test_get_projects(client: AsyncClient, db: AsyncSession):

    test_project_two = {
        "url": "https://github.com/benthomasson/eda-project",
        "name": "Test Name TWO",
        "description": "This is a test description two",
    }

    test_projects = [TEST_PROJECT, test_project_two]

    for test_project in test_projects:
        query = sa.insert(models.projects).values(
            url=test_project["url"],
            name=test_project["name"],
            description=test_project["description"],
        )
        await db.execute(query)

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 2

    response = await client.get("/api/projects/")

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == TEST_PROJECT["name"]
    assert data[1]["url"] == test_project_two["url"]
