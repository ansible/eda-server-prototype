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
async def test_create_delete_job(client: AsyncClient, db: AsyncSession):
    query = sa.insert(models.job_instances).values(
        uuid="f4c87c90-254e-11ed-861d-0242ac120002",
    )
    await db.execute(query)

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    jobs_len = len(jobs)

    job_to_delete = (await db.execute(sa.select(models.job_instances))).first()
    job_id = job_to_delete.id

    response = await client.delete(f"/api/job_instance/{job_id}")
    assert response.status_code == status_codes.HTTP_204_NO_CONTENT

    jobs = (await db.execute(sa.select(models.job_instances))).all()
    assert len(jobs) == (jobs_len - 1)


@pytest.mark.asyncio
async def test_delete_job_not_found(client: AsyncClient):
    response = await client.delete("/api/job_instance/1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND
