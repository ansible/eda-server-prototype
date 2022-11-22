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

# TODO(cutwater): Add unit tests for API endpoints
from unittest import mock

from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.sql import base as bsql
from eda_server.types import Action, ResourceType

TEST_PROJECT = {
    "url": "https://git.example.com/sample/test-project",
    "name": "Test Name",
    "description": "This is a test description",
}


TEST_PLAYBOOK = """
---
- name: hello
  hosts: localhost
  gather_facts: false
  tasks:
    - debug:
        msg: hello
"""


async def _create_playbooks(db: AsyncSession):
    (project_id,) = (
        await bsql.insert_object(
            db,
            models.projects,
            values=TEST_PROJECT,
        )
    ).inserted_primary_key

    (playbook_id,) = (
        await bsql.insert_object(
            db,
            models.playbooks,
            values={
                "name": "hello.yml",
                "playbook": TEST_PLAYBOOK,
                "project_id": project_id,
            },
        )
    ).inserted_primary_key

    foreign_keys = {
        "project_id": project_id,
        "playbook_id": playbook_id,
    }

    return foreign_keys


async def test_list_playbooks(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    fks = await _create_playbooks(db)
    await db.commit()

    response = await client.get(
        "/api/playbooks/",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    playbooks = response.json()
    assert type(playbooks) is list
    assert len(playbooks) > 0

    playbook = playbooks[0]
    assert playbook["id"] == fks["playbook_id"]
    assert playbook["name"] == "hello.yml"
    assert playbook["project_id"] == fks["project_id"]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PLAYBOOK, Action.READ
    )


async def test_list_playbooks_empty_response(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get(
        "/api/playbooks/",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    activations = response.json()
    assert activations == []

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PLAYBOOK, Action.READ
    )


async def test_read_playbook(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    fks = await _create_playbooks(db)
    await db.commit()

    playbook_id = fks["playbook_id"]
    response = await client.get(
        f"/api/playbook/{playbook_id}",
    )
    assert response.status_code == status_codes.HTTP_200_OK
    playbook = response.json()
    assert "id" in playbook

    assert playbook["name"] == "hello.yml"
    assert playbook["id"] == fks["playbook_id"]
    assert playbook["project_id"] == fks["project_id"]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PLAYBOOK, Action.READ
    )


async def test_read_playbook_not_found(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.get("/api/playbook/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.PLAYBOOK, Action.READ
    )
