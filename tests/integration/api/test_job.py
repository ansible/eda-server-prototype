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

from unittest import mock

import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.sql import base as bsql
from eda_server.managers import taskmanager
from eda_server.types import Action, InventorySource, ResourceType

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
JOB_UUID = "f4c87c90-254e-11ed-861d-0242ac120002"


async def _create_dependent_objects(db: AsyncSession):
    (extra_var_id,) = (
        await bsql.insert_object(
            db,
            models.extra_vars,
            values={"name": "vars.yml", "extra_var": TEST_EXTRA_VAR},
        )
    ).inserted_primary_key

    (inventory_id,) = (
        await bsql.insert_object(
            db,
            models.inventories,
            values={
                "name": "inventory.yml",
                "inventory": TEST_INVENTORY,
                "inventory_source": InventorySource.USER_DEFINED.value,
            },
        )
    ).inserted_primary_key

    (rulebook_id,) = (
        await bsql.insert_object(
            db,
            models.rulebooks,
            values={"name": "ruleset.yml", "rulesets": TEST_RULEBOOK},
        )
    ).inserted_primary_key

    (project_id,) = (
        await bsql.insert_object(
            db,
            models.projects,
            values={
                "url": "https://github.com/ansible/event-driven-ansible",
                "name": "test",
                "description": "test",
            },
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
        "extra_var_id": extra_var_id,
        "inventory_id": inventory_id,
        "rulebook_id": rulebook_id,
        "project_id": project_id,
        "playbook_id": playbook_id,
    }

    return foreign_keys


async def _create_job_instance(db: AsyncSession, foreign_keys: dict):
    (job_instance_id,) = (
        await bsql.insert_object(
            db,
            models.job_instances,
            values={
                "name": "test_job_instance",
                "uuid": JOB_UUID,
            },
        )
    ).inserted_primary_key

    return job_instance_id


@mock.patch("asyncio.create_task")
async def test_create_job_instance(
    create_task: mock.Mock,
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    fks = await _create_dependent_objects(db)
    await db.commit()

    response = await client.post(
        "/api/job_instance",
        json={
            "playbook_id": fks["playbook_id"],
            "inventory_id": fks["inventory_id"],
            "extra_var_id": fks["extra_var_id"],
        },
    )

    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()

    assert data["playbook_id"] == fks["playbook_id"]
    assert data["inventory_id"] == fks["inventory_id"]
    assert data["extra_var_id"] == fks["extra_var_id"]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.CREATE
    )

    # clear tasks for the test of listing tasks
    taskmanager.tasks.clear()


# Suppress warnings from asyncio.create_task when calling coroutines
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_read_job(
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    fks = await _create_dependent_objects(db)
    job_instance_id = await _create_job_instance(db, fks)

    response = await client.get(
        f"/api/job_instance/{job_instance_id}",
    )

    assert response.status_code == status_codes.HTTP_200_OK

    job_instance = response.json()
    assert job_instance["uuid"] == JOB_UUID
    assert job_instance["name"] == "test_job_instance"

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.READ
    )


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_read_job_not_found(
    client: AsyncClient,
    check_permission_spy: mock.Mock,
):
    response = await client.get("/api/job_instance/42")

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.READ
    )


async def test_list_job(
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    fks = await _create_dependent_objects(db)
    job_instance_id = await _create_job_instance(db, fks)

    response = await client.get("/api/job_instances")

    assert response.status_code == status_codes.HTTP_200_OK

    job_instances = response.json()
    assert type(job_instances) is list
    assert len(job_instances) > 0

    job_instance = job_instances[0]

    assert job_instance["id"] == job_instance_id
    assert job_instance["uuid"] == JOB_UUID
    assert job_instance["name"] == "test_job_instance"

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.READ
    )


async def test_list_job_empty_response(
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    response = await client.get("/api/job_instances")

    assert response.status_code == status_codes.HTTP_200_OK

    job_instances = response.json()
    assert job_instances == []

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.READ
    )


async def test_read_job_instance_events(
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    fks = await _create_dependent_objects(db)
    job_instance_id = await _create_job_instance(db, fks)

    response = await client.get(
        f"/api/job_instance_events/{job_instance_id}",
    )

    assert response.status_code == status_codes.HTTP_200_OK

    job_instance_events = response.json()

    assert type(job_instance_events) is list
    assert job_instance_events == []

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.READ
    )


async def test_read_job_instance_events_not_found(
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    response = await client.get(
        "/api/job_instance_events/42",
    )

    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.READ
    )


async def test_delete_job(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    fks = await _create_dependent_objects(db)
    job_instance_id = await _create_job_instance(db, fks)
    await db.commit()

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    jobs_len = len(jobs)

    response = await client.delete(f"/api/job_instance/{job_instance_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    assert len(jobs) == (jobs_len - 1)

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.DELETE
    )


async def test_delete_job_not_found(
    client: AsyncClient, check_permission_spy: mock.Mock
):
    response = await client.delete("/api/job_instance/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.DELETE
    )


@mock.patch("eda_server.ruleset.activate_rulesets")
async def test_rerun_job_with_needed(
    activate_rulesets: mock.Mock,
    client: AsyncClient,
    db: AsyncSession,
    check_permission_spy: mock.Mock,
):
    # prepare job_instance
    query = sa.insert(models.job_instances).values(
        uuid="f4c87c90-254e-11ed-861d-0242ac120002", name="dummy-playbooks"
    )
    job_instance_id = (await db.execute(query)).inserted_primary_key[0]

    await client.post(f"/api/job_instance/{job_instance_id}")

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.CREATE
    )


async def test_rerun_job_miss_job_instance(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    invalid_job_id = 10
    response = await client.post(f"/api/job_instance/{invalid_job_id}")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"] == f"Job instance {invalid_job_id} not found"

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.CREATE
    )


@mock.patch(
    "eda_server.ruleset.activate_rulesets",
    side_effect=Exception("Test exception"),
)
async def test_rerun_job_with_exception(client: AsyncClient, db: AsyncSession):
    # prepare job_instance
    invalid_playbook_name = "miss-playbooks"
    query = sa.insert(models.job_instances).values(
        uuid="f4c87c90-254e-11ed-861d-0242ac120002", name=invalid_playbook_name
    )
    job_instance_id = (await db.execute(query)).inserted_primary_key[0]

    response = await client.post(f"/api/job_instance/{job_instance_id}")
    with pytest.raises(Exception):
        assert (
            response.status_code == status_codes.HTTP_500_INTERNAL_SERVER_ERROR
        )
