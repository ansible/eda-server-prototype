import datetime

import pytest
import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ansible_events_ui.db import models

TEST_AUDIT_RULE = {
    "name": "test-audit-rule",
    "definition": {"test": "test"},
    "status": "successful",
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

TEST_AUDIT_RULE_JOB = {
    "uuid": "f4c87c90-254e-11ed-861d-0242ac120005",
}

TEST_AUDIT_RULE_JOB_EVENT = {
    "job_uuid": "f4c87c90-254e-11ed-861d-0242ac120005",
    "counter": 1,
    "type": "playbook_on_start",
    "created_at": datetime.datetime.now(),
    "stdout": "foo",
}

TEST_AUDIT_RULE_JOB_HOST = {
    "job_uuid": "f4c87c90-254e-11ed-861d-0242ac120005",
    "host": "localhost",
    "playbook": "test_playbook",
    "play": "hello",
    "task": "debug",
    "status": "success",
}

RULE_NAMES = {
    "rulebook_name": "ruleset.yml",
    "ruleset_name": "Test simple",
}


async def _create_activation_dependent_objects(
    client: AsyncClient, db: AsyncSession
):
    (extra_var_id,) = (
        await db.execute(
            sa.insert(models.extra_vars).values(
                name="vars.yml", extra_var=TEST_EXTRA_VAR
            )
        )
    ).inserted_primary_key

    (inventory_id,) = (
        await db.execute(
            sa.insert(models.inventories).values(
                name="inventory.yml", inventory=TEST_INVENTORY
            )
        )
    ).inserted_primary_key

    (rulebook_id,) = (
        await db.execute(
            sa.insert(models.rulebooks).values(
                name=RULE_NAMES["rulebook_name"], rulesets=TEST_RULEBOOK
            )
        )
    ).inserted_primary_key

    (ruleset_id,) = (
        await db.execute(
            sa.insert(models.rulesets).values(
                name=RULE_NAMES["ruleset_name"],
                rulebook_id=rulebook_id,
            )
        )
    ).inserted_primary_key

    (rule_id,) = (
        await db.execute(
            sa.insert(models.rules).values(
                name=None, action={"debug": None}, ruleset_id=ruleset_id
            )
        )
    ).inserted_primary_key

    (activation_instance_id,) = (
        await db.execute(
            sa.insert(models.activation_instances).values(
                name="test-activation",
                rulebook_id=rulebook_id,
                inventory_id=inventory_id,
                extra_var_id=extra_var_id,
            )
        )
    ).inserted_primary_key

    (job_instance_id,) = (
        await db.execute(
            sa.insert(models.job_instances).values(
                uuid=TEST_AUDIT_RULE_JOB["uuid"],
            )
        )
    ).inserted_primary_key

    (job_instance_event_id,) = (
        await db.execute(
            sa.insert(models.job_instance_events).values(
                job_uuid=TEST_AUDIT_RULE_JOB_EVENT["job_uuid"],
                counter=TEST_AUDIT_RULE_JOB_EVENT["counter"],
                type=TEST_AUDIT_RULE_JOB_EVENT["type"],
                created_at=TEST_AUDIT_RULE_JOB_EVENT["created_at"],
                stdout=TEST_AUDIT_RULE_JOB_EVENT["stdout"],
            )
        )
    ).inserted_primary_key

    (job_instance_host_id,) = (
        await db.execute(
            sa.insert(models.job_instance_hosts).values(
                job_uuid=TEST_AUDIT_RULE_JOB_HOST["job_uuid"],
                host=TEST_AUDIT_RULE_JOB_HOST["host"],
                playbook=TEST_AUDIT_RULE_JOB_HOST["playbook"],
                play=TEST_AUDIT_RULE_JOB_HOST["play"],
                task=TEST_AUDIT_RULE_JOB_HOST["task"],
                status=TEST_AUDIT_RULE_JOB_HOST["status"],
            )
        )
    ).inserted_primary_key

    foreign_keys = {
        "extra_var_id": extra_var_id,
        "inventory_id": inventory_id,
        "rulebook_id": rulebook_id,
        "ruleset_id": ruleset_id,
        "rule_id": rule_id,
        "activation_instance_id": activation_instance_id,
        "job_instance_id": job_instance_id,
        "job_instance_event_id": job_instance_event_id,
        "job_instance_host_id": job_instance_host_id,
    }

    return foreign_keys


async def _create_audit_rule(
    client: AsyncClient, db: AsyncSession, foreign_keys
):

    (audit_rule_id,) = (
        await db.execute(
            sa.insert(models.audit_rules).values(
                name=TEST_AUDIT_RULE["name"],
                definition=TEST_AUDIT_RULE["definition"],
                status=TEST_AUDIT_RULE["status"],
                activation_instance_id=foreign_keys["activation_instance_id"],
                ruleset_id=foreign_keys["ruleset_id"],
                rule_id=foreign_keys["rule_id"],
                job_instance_id=foreign_keys["job_instance_id"],
                fired_date=datetime.datetime.now(),
            )
        )
    ).inserted_primary_key

    return audit_rule_id


@pytest.mark.asyncio
async def test_read_audit_rule_jobs(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    audit_rule_id = await _create_audit_rule(client, db, foreign_keys)

    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1

    response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/jobs",
    )
    audit_jobs = response.json()
    assert response.status_code == status_codes.HTTP_200_OK
    assert type(audit_jobs) == list
    assert len(audit_jobs) == 1
    job = audit_jobs[0]
    assert job["id"] == foreign_keys["job_instance_id"]
    assert job["status"] == TEST_AUDIT_RULE["status"]


@pytest.mark.asyncio
async def test_read_audit_details(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    audit_rule_id = await _create_audit_rule(client, db, foreign_keys)
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1

    response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/details",
    )
    audit_rule = response.json()
    assert response.status_code == status_codes.HTTP_200_OK
    assert audit_rule["name"] == TEST_AUDIT_RULE["name"]
    assert audit_rule["definition"] == TEST_AUDIT_RULE["definition"]
    assert audit_rule["status"] == TEST_AUDIT_RULE["status"]
    assert audit_rule["activation"] == {
        "id": foreign_keys["activation_instance_id"],
        "name": "test-activation",
    }
    assert audit_rule["ruleset"] == {
        "id": foreign_keys["ruleset_id"],
        "name": RULE_NAMES["ruleset_name"],
    }
    assert audit_rule["definition"] == TEST_AUDIT_RULE["definition"]


@pytest.mark.asyncio
async def test_read_audit_rule_events(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    audit_rule_id = await _create_audit_rule(client, db, foreign_keys)
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1

    response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/events",
    )
    audit_job_events = response.json()
    assert response.status_code == status_codes.HTTP_200_OK
    assert type(audit_job_events) == list
    assert len(audit_job_events) == 1
    job_event = audit_job_events[0]
    assert job_event["id"] == foreign_keys["job_instance_event_id"]
    assert job_event["type"] == TEST_AUDIT_RULE_JOB_EVENT["type"]
    assert (
        job_event["increment_counter"] == TEST_AUDIT_RULE_JOB_EVENT["counter"]
    )
    assert job_event["name"] == TEST_AUDIT_RULE["name"]


@pytest.mark.asyncio
async def test_read_audit_rule_hosts(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(client, db)
    audit_rule_id = await _create_audit_rule(client, db, foreign_keys)
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1

    response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/hosts",
    )
    audit_hosts = response.json()
    assert response.status_code == status_codes.HTTP_200_OK
    assert type(audit_hosts) == list
    assert len(audit_hosts) == 1
    host = audit_hosts[0]
    assert host["id"] == foreign_keys["job_instance_host_id"]
    assert host["name"] == TEST_AUDIT_RULE_JOB_HOST["host"]
    assert host["status"] == TEST_AUDIT_RULE_JOB_HOST["status"]


@pytest.mark.asyncio
async def test_audit_rule_404(client: AsyncClient, db: AsyncSession):
    audit_rule_id = 100
    details_response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/details",
    )
    jobs_response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/jobs",
    )
    events_response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/events",
    )
    hosts_response = await client.get(
        f"/api/audit/rule/{audit_rule_id}/hosts",
    )
    assert details_response.status_code == status_codes.HTTP_404_NOT_FOUND
    assert jobs_response.status_code == status_codes.HTTP_404_NOT_FOUND
    assert events_response.status_code == status_codes.HTTP_404_NOT_FOUND
    assert hosts_response.status_code == status_codes.HTTP_404_NOT_FOUND
