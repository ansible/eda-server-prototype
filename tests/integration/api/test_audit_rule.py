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

import datetime
from unittest import mock

import sqlalchemy as sa
from fastapi import status as status_codes
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.types import Action, InventorySource, ResourceType

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


async def _create_activation_dependent_objects(db: AsyncSession):
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
                name="inventory.yml",
                inventory=TEST_INVENTORY,
                inventory_source=InventorySource.USER_DEFINED,
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


async def _create_audit_rule(db: AsyncSession, foreign_keys):

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


async def test_read_audit_rule_jobs(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    audit_rule_id = await _create_audit_rule(db, foreign_keys)

    # REVIEW(cutwater): This assert statement tests the test case itself
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1
    await db.commit()

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
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.AUDIT_RULE, Action.READ
    )


async def test_read_audit_details(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    audit_rule_id = await _create_audit_rule(db, foreign_keys)

    # REVIEW(cutwater): This assert statement tests the test case itself
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1

    await db.commit()

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
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.AUDIT_RULE, Action.READ
    )


async def test_read_audit_rule_events(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    audit_rule_id = await _create_audit_rule(db, foreign_keys)

    # REVIEW(cutwater): This assert statement tests the test case itself
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1

    await db.commit()

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
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.AUDIT_RULE, Action.READ
    )


async def test_read_audit_rule_hosts(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    foreign_keys = await _create_activation_dependent_objects(db)
    audit_rule_id = await _create_audit_rule(db, foreign_keys)

    # REVIEW(cutwater): This assert statement tests the test case itself
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 1

    await db.commit()

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
    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.AUDIT_RULE, Action.READ
    )


async def test_list_audit_rules_fired(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(db)
    await _create_audit_rule(db, foreign_keys)
    await _create_audit_rule(db, foreign_keys)

    # REVIEW(cutwater): This assert statement tests the test case itself
    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 2

    await db.commit()

    response = await client.get("/api/audit/rules_fired")
    fired_rules = response.json()

    assert response.status_code == status_codes.HTTP_200_OK
    assert type(fired_rules) == list
    assert len(fired_rules) == 2
    rule = fired_rules[0]
    assert rule["name"] == TEST_AUDIT_RULE["name"]
    assert rule["job"] == TEST_AUDIT_RULE_JOB_HOST["task"]
    assert rule["status"] == TEST_AUDIT_RULE["status"]
    assert rule["ruleset"] == RULE_NAMES["ruleset_name"]
    assert fired_rules[0]["fired_date"] > fired_rules[1]["fired_date"]


async def test_list_audit_hosts_changed(client: AsyncClient, db: AsyncSession):
    foreign_keys = await _create_activation_dependent_objects(db)
    await _create_audit_rule(db, foreign_keys)
    await _create_audit_rule(db, foreign_keys)

    audit_rules = (await db.execute(sa.select(models.audit_rules))).all()
    assert len(audit_rules) == 2

    response = await client.get("/api/audit/hosts_changed")
    fired_rules = response.json()

    assert response.status_code == status_codes.HTTP_200_OK
    assert type(fired_rules) == list
    assert len(fired_rules) == 2
    rule = fired_rules[0]
    assert rule["host"] == TEST_AUDIT_RULE_JOB_HOST["host"]
    assert rule["rule"] == TEST_AUDIT_RULE["name"]
    assert rule["ruleset"] == RULE_NAMES["ruleset_name"]
    assert fired_rules[0]["fired_date"] > fired_rules[1]["fired_date"]


async def test_empty_responses(client: AsyncClient, db: AsyncSession):
    fired_rules_response = await client.get(
        "/api/audit/rules_fired",
    )
    fired_hosts_response = await client.get(
        "/api/audit/hosts_changed",
    )

    assert fired_rules_response.json() == []
    assert fired_hosts_response.json() == []


async def test_audit_rule_404(client: AsyncClient):
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
