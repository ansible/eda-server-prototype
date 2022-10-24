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

import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, ResourceType

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


async def test_create_delete_job(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    query = sa.insert(models.job_instances).values(
        uuid="f4c87c90-254e-11ed-861d-0242ac120002",
    )
    await db.execute(query)

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    jobs_len = len(jobs)

    job_to_delete = (await db.execute(sa.select(models.job_instances))).first()
    job_id = job_to_delete.id

    await db.commit()

    response = await client.delete(f"/api/job_instance/{job_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    assert len(jobs) == (jobs_len - 1)

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.JOB, Action.DELETE
    )


async def test_delete_job_not_found(client: AsyncClient):
    response = await client.delete("/api/job_instance/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_rerun_job_with_needed(client: AsyncClient, db: AsyncSession):
    # prepare project
    query = sa.insert(models.projects).values(name="dummy-project")
    project_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare inventory
    query = sa.insert(models.inventories).values(
        name="dummy-inventories",
        inventory=TEST_INVENTORY,
        project_id=project_id,
    )
    inventory_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare extra_var
    query = sa.insert(models.extra_vars).values(
        name="dummy-extravars", extra_var=TEST_EXTRA_VAR, project_id=project_id
    )
    extra_var_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare activation_instance
    query = sa.insert(models.activation_instances).values(
        name="dummy-activation_instances",
        inventory_id=inventory_id,
        project_id=project_id,
        extra_var_id=extra_var_id,
    )
    activation_instance_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare job_instance
    query = sa.insert(models.job_instances).values(
        uuid="f4c87c90-254e-11ed-861d-0242ac120002", name="dummy-playbooks"
    )
    job_instance_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare relation between job_instance and activation_instance
    query = sa.insert(models.activation_instance_job_instances).values(
        activation_instance_id=activation_instance_id,
        job_instance_id=job_instance_id,
    )
    await db.execute(query)

    # prepare playbook
    query = sa.insert(models.playbooks).values(
        name="dummy-playbooks", playbook=TEST_PLAYBOOK, project_id=project_id
    )
    playbook_id = (await db.execute(query)).inserted_primary_key[0]

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    jobs_len = len(jobs)

    response = await client.post(f"/api/job_instance/{job_instance_id}")
    assert response.status_code == status_codes.HTTP_200_OK

    data = response.json()
    assert data["playbook_id"] == playbook_id
    assert data["inventory_id"] == inventory_id
    assert data["extra_var_id"] == extra_var_id

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    assert len(jobs) == (jobs_len + 1)


async def test_rerun_job_miss_job_instance(
    client: AsyncClient, db: AsyncSession
):
    invalid_job_id = 10
    response = await client.post(f"/api/job_instance/{invalid_job_id}")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"] == f"Job instance {invalid_job_id} not found"


async def test_rerun_job_miss_playbook(client: AsyncClient, db: AsyncSession):
    # prepare project
    query = sa.insert(models.projects).values(name="dummy-project")
    project_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare inventory
    query = sa.insert(models.inventories).values(
        name="dummy-inventories",
        inventory=TEST_INVENTORY,
        project_id=project_id,
    )
    inventory_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare extra_var
    query = sa.insert(models.extra_vars).values(
        name="dummy-extravars", extra_var=TEST_EXTRA_VAR, project_id=project_id
    )
    extra_var_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare activation_instance
    query = sa.insert(models.activation_instances).values(
        name="dummy-activation_instances",
        inventory_id=inventory_id,
        project_id=project_id,
        extra_var_id=extra_var_id,
    )
    activation_instance_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare job_instance
    invalid_playbook_name = "miss-playbooks"
    query = sa.insert(models.job_instances).values(
        uuid="f4c87c90-254e-11ed-861d-0242ac120002", name=invalid_playbook_name
    )
    job_instance_id = (await db.execute(query)).inserted_primary_key[0]

    # prepare relation between job_instance and activation_instance
    query = sa.insert(models.activation_instance_job_instances).values(
        activation_instance_id=activation_instance_id,
        job_instance_id=job_instance_id,
    )
    await db.execute(query)

    response = await client.post(f"/api/job_instance/{job_instance_id}")
    assert response.status_code == status_codes.HTTP_400_BAD_REQUEST

    data = response.json()
    assert data["detail"] == f"Playbook {invalid_playbook_name} not found"
