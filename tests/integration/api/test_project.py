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

import hashlib
from unittest import mock

import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, InventorySource, ResourceType

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


async def test_delete_project(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )
    result = await db.execute(query)
    (project_id,) = result.inserted_primary_key

    query = sa.insert(models.extra_vars).values(
        name="vars.yml",
        extra_var=TEST_EXTRA_VAR,
        project_id=project_id,
    )
    await db.execute(query)

    query = sa.insert(models.inventories).values(
        name="inventory.yml",
        inventory=TEST_INVENTORY,
        inventory_source=InventorySource.PROJECT,
        project_id=project_id,
    )
    await db.execute(query)

    query = sa.insert(models.rulebooks).values(
        name="ruleset.yml",
        rulesets=TEST_RULEBOOK,
        project_id=project_id,
    )
    await db.execute(query)

    query = sa.insert(models.playbooks).values(
        name="hello.yml",
        playbook=TEST_PLAYBOOK,
        project_id=project_id,
    )
    await db.execute(query)
    await db.commit()

    response = await client.delete(f"/api/projects/{project_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT
    assert 0 == await db.scalar(
        sa.select(func.count()).select_from(models.projects)
    )
    assert 0 == await db.scalar(
        sa.select(func.count()).select_from(models.extra_vars)
    )
    assert 0 == await db.scalar(
        sa.select(func.count()).select_from(models.inventories)
    )
    assert 0 == await db.scalar(
        sa.select(func.count()).select_from(models.rulebooks)
    )
    assert 0 == await db.scalar(
        sa.select(func.count()).select_from(models.playbooks)
    )

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PROJECT, Action.DELETE
    )


async def test_delete_project_not_found(client: AsyncClient):
    response = await client.delete("/api/projects/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


@mock.patch("tempfile.TemporaryDirectory")
@mock.patch("eda_server.project.clone_project")
@mock.patch("eda_server.project.find_project_files")
@mock.patch("eda_server.project.import_project_files")
@mock.patch("eda_server.project.tar_project")
async def test_create_project(
    tar_project: mock.Mock,
    import_project_files: mock.Mock,
    find_project_files: mock.Mock,
    clone_project: mock.Mock,
    tempfile: mock.Mock(),
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    project_files = {"rulebook": [("rulebook", "test-rules.yml")]}
    repo_dir = "/tmp/test-create-project"
    tempfile.return_value.__enter__.return_value = repo_dir
    find_project_files.return_value = project_files
    found_hash = hashlib.sha1(b"test").hexdigest()
    clone_project.return_value = found_hash

    response = await client.post(
        "/api/projects",
        json=TEST_PROJECT,
    )
    assert response.status_code == status_codes.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["name"] == TEST_PROJECT["name"]

    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]
    assert project["id"] == data["id"]
    assert project["name"] == TEST_PROJECT["name"]
    assert project["url"] == TEST_PROJECT["url"]

    clone_project.assert_called_once_with(TEST_PROJECT["url"], mock.ANY)
    import_project_files.assert_called_once_with(db, mock.ANY, project["id"])
    find_project_files.assert_called_once_with(repo_dir)
    tar_project.assert_called_once_with(db, project["large_data_id"], repo_dir)
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PROJECT, Action.CREATE
    )


@mock.patch("tempfile.TemporaryDirectory")
@mock.patch("eda_server.project.clone_project")
@mock.patch("eda_server.project.find_project_files")
@mock.patch(
    "builtins.open", new_callable=mock.mock_open, read_data="test data"
)
@mock.patch("eda_server.project.retrieve_existing_project_files")
@mock.patch("eda_server.project.import_project_file")
async def test_sync_project(
    import_project_file: mock.Mock,
    retrieve_existing_project_files: mock.Mock,
    project_file: mock.mock_open,
    find_project_files: mock.Mock,
    clone_project: mock.Mock,
    tempfile: mock.Mock(),
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    old_hash = hashlib.sha1(b"test").hexdigest()
    query = sa.insert(models.projects).values(
        git_hash=old_hash,
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )
    (project_id,) = (await db.execute(query)).inserted_primary_key
    await db.commit()

    file_type = "rulebook"
    filename = "test-rules.yml"
    new_files = [("rulebook", filename)]
    project_files = {file_type: new_files}
    repo_dir = "/tmp/test-sync-project"

    tempfile.return_value.__enter__.return_value = repo_dir
    find_project_files.return_value = project_files
    new_hash = hashlib.sha1(b"test2").hexdigest()
    clone_project.return_value = new_hash

    response = await client.post(f"/api/projects/{project_id}")
    assert response.status_code == status_codes.HTTP_200_OK

    (_hash,) = (
        await db.execute(
            sa.select(models.projects.c.git_hash).where(
                models.projects.c.id == project_id
            )
        )
    ).one_or_none()
    assert _hash == new_hash

    find_project_files.assert_called_once_with(repo_dir)
    retrieve_existing_project_files.assert_called_once_with(db, project_id)
    assert open(repo_dir).read() == "test data"
    project_file.assert_called_with(repo_dir)
    import_project_file.assert_called_once_with(
        db, filename, "test data", file_type, project_id
    )
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PROJECT, Action.UPDATE
    )


async def test_create_project_bad_entity(client: AsyncClient):
    bad_project = {
        "url": None,
        "name": "Test Name",
        "description": "This is a test description",
    }
    response = await client.post(
        "/api/projects",
        json=bad_project,
    )
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


@mock.patch("eda_server.project.clone_project")
async def test_create_project_unique_name(
    clone_project: mock.Mock,
    client: AsyncClient,
    db: AsyncSession,
):
    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )
    await db.execute(query)
    await db.commit()

    found_hash = hashlib.sha1(b"test").hexdigest()
    clone_project.return_value = found_hash, "/tmp/test-create-project"

    response = await client.post(
        "/api/projects",
        json=TEST_PROJECT,
    )
    assert response.status_code == status_codes.HTTP_409_CONFLICT
    data = response.json()
    assert (
        data["detail"]
        == f"Project with name '{TEST_PROJECT['name']}' already exists"
    )


async def test_create_project_bad_name(client: AsyncClient):
    test_project_bad = TEST_PROJECT.copy()
    test_project_bad["name"] = "     "
    response = await client.post("/api/projects", json=test_project_bad)
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY

    test_project_bad["name"] = ""
    response = await client.post("/api/projects", json=test_project_bad)
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


async def test_create_project_missing_name(client: AsyncClient):
    test_project_bad = TEST_PROJECT.copy()
    del test_project_bad["name"]
    response = await client.post("/api/projects", json=test_project_bad)
    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


async def test_read_project(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )
    await db.execute(query)

    # REVIEW(cutwater): This assert statement tests the test case itself
    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]

    await db.commit()

    response = await client.get(f"/api/projects/{project['id']}")

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert data["name"] == TEST_PROJECT["name"]
    assert data["url"] == TEST_PROJECT["url"]
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PROJECT, Action.READ
    )


async def test_read_project_not_found(client: AsyncClient, db: AsyncSession):
    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )
    await db.execute(query)
    await db.commit()

    response = await client.get("/api/projects/100")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_update_project(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    query = sa.insert(models.projects).values(
        url=TEST_PROJECT["url"],
        name=TEST_PROJECT["name"],
        description=TEST_PROJECT["description"],
    )
    await db.execute(query)

    # REVIEW(cutwater): This assert statement tests the test case itself
    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 1
    project = projects[0]

    await db.commit()

    response = await client.patch(
        f"/api/projects/{project['id']}",
        json={"name": "new test name"},
    )

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert data["name"] == "new test name"
    assert data["url"] == TEST_PROJECT["url"]
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PROJECT, Action.UPDATE
    )


async def test_update_project_missing(client: AsyncClient):

    response = await client.patch(
        "/api/projects/-1",
        json={"name": "new test name"},
    )

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_update_project_bad_name(client: AsyncClient):

    response = await client.patch(
        "/api/projects/1",
        json={"name": ""},
    )

    assert response.status_code == status_codes.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_project_unique_name(
    client: AsyncClient, db: AsyncSession
):

    test_projects_values = [
        {
            "url": TEST_PROJECT["url"],
            "name": TEST_PROJECT["name"],
            "description": TEST_PROJECT["description"],
        },
        {
            "url": TEST_PROJECT["url"] + "/",
            "name": TEST_PROJECT["name"] + " 2",
            "description": TEST_PROJECT["description"] + " 2",
        },
    ]
    query = (
        sa.insert(models.projects)
        .values(test_projects_values)
        .returning(models.projects)
    )
    test_projects = (await db.execute(query)).all()
    assert len(test_projects) == 2

    # Including same name as already in DB passes
    test_project = {
        k: v.isoformat() if k.endswith("_at") else v
        for k, v in test_projects[0]._asdict().items()
    }
    test_project["description"] = "updated-1"
    updated_values = {
        "name": test_project["name"],
        "description": test_project["description"],
    }
    await db.commit()

    response = await client.patch(
        f"/api/projects/{test_project['id']}",
        json=updated_values,
    )
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    del test_project["large_data_id"]
    assert data == test_project

    # Rename project.name to same name as a different project will conflict
    test_project = {
        k: v.isoformat() if k.endswith("_at") else v
        for k, v in test_projects[1]._asdict().items()
    }
    test_project["name"] = test_projects[0].name
    test_project["description"] = "updated-2"
    updated_values = {
        "name": test_project["name"],
        "description": test_project["description"],
    }
    response = await client.patch(
        f"/api/projects/{test_project['id']}",
        json=updated_values,
    )
    assert response.status_code == status_codes.HTTP_409_CONFLICT
    data = response.json()
    expected_msg = "Project with name '{0}' already exists".format(
        test_project["name"]
    )
    assert data["detail"] == expected_msg


async def test_list_projects(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):

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

    # REVIEW(cutwater): This assert statement tests the test case itself
    projects = (await db.execute(sa.select(models.projects))).all()
    assert len(projects) == 2

    await db.commit()

    response = await client.get("/api/projects")

    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == TEST_PROJECT["name"]
    assert data[1]["url"] == test_project_two["url"]
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PROJECT, Action.READ
    )
