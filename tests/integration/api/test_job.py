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
