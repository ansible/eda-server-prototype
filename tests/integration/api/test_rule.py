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

from collections import namedtuple
from datetime import datetime, timedelta, timezone
from typing import Tuple
from unittest import mock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as status_codes

from eda_server.db import models
from eda_server.db.sql import base as bsql
from eda_server.types import Action, InventorySource, ResourceType

TEST_RULESET_SIMPLE = """
---
- name: Test simple
  hosts: all
  sources:
    - name: range
      range:
        limit: 5
  rules:
    - name:
      condition: event.i == 1
      action:
        debug:
"""


DBTestData = namedtuple(
    "DBTestData",
    (
        "project",
        "rulebook",
        "ruleset",
        "rules",
        "inventory",
        "activation_instance",
        "audit_rules",
    ),
)


async def _create_rules(db: AsyncSession, intervals: Tuple[int, int] = (5, 6)):
    project = (
        await bsql.insert_object(
            db,
            models.projects,
            values={"name": "project--test-ruleset-1.yml"},
            returning=[models.projects.c.id, models.projects.c.name],
        )
    ).one()

    rulebook = (
        await bsql.insert_object(
            db,
            models.rulebooks,
            values={
                "name": "test--ruleset-1.yml",
                "rulesets": TEST_RULESET_SIMPLE,
                "project_id": project.id,
            },
            returning=[models.rulebooks.c.id, models.rulebooks.c.name],
        )
    ).one()

    ruleset = (
        await bsql.insert_object(
            db,
            models.rulesets,
            values={
                "name": "Test--simple",
                "rulebook_id": rulebook.id,
                "sources": [
                    {
                        "name": "range",
                        "type": "range",
                        "source": "range",
                        "config": {"limit": 5},
                    }
                ],
            },
            returning=[
                models.rulesets.c.id,
                models.rulesets.c.name,
                models.rulesets.c.rulebook_id,
                models.rulesets.c.created_at,
                models.rulesets.c.modified_at,
                models.rulesets.c.sources,
            ],
        )
    ).one()

    rules = (
        await bsql.insert_object(
            db,
            models.rules,
            values=[
                {
                    "name": "rule--1",
                    "action": {"debug": None},
                    "ruleset_id": ruleset.id,
                },
                {
                    "name": "rule--2",
                    "action": {"debug": "eek"},
                    "ruleset_id": ruleset.id,
                },
            ],
            returning=[
                models.rules.c.id,
                models.rules.c.name,
                models.rules.c.action,
                models.rules.c.ruleset_id,
            ],
        )
    ).all()

    inventory = (
        await bsql.insert_object(
            db,
            models.inventories,
            values={
                "name": "tst-inv-1",
                "project_id": project.id,
                "inventory_source": InventorySource.PROJECT,
            },
            returning=[models.inventories],
        )
    ).one()

    activation_instance = (
        await bsql.insert_object(
            db,
            models.activation_instances,
            values={
                "name": "act-inst-1",
                "rulebook_id": rulebook.id,
                "inventory_id": inventory.id,
            },
            returning=[models.activation_instances],
        )
    ).one()

    audit_rules = (
        await bsql.insert_object(
            db,
            models.audit_rules,
            values=[
                {
                    "name": rules[0].name,
                    "description": "",
                    "status": "success",
                    "fired_date": datetime.utcnow().replace(
                        tzinfo=timezone.utc
                    )
                    - timedelta(days=intervals[0]),
                    "created_at": datetime.utcnow().replace(
                        tzinfo=timezone.utc
                    ),
                    "definition": rules[0].action,
                    "rule_id": rules[0].id,
                    "ruleset_id": ruleset.id,
                    "activation_instance_id": activation_instance.id,
                    "job_instance_id": None,
                },
                {
                    "name": rules[1].name,
                    "description": "",
                    "status": "success",
                    "fired_date": datetime.utcnow().replace(
                        tzinfo=timezone.utc
                    )
                    - timedelta(days=intervals[1]),
                    "created_at": datetime.utcnow().replace(
                        tzinfo=timezone.utc
                    ),
                    "definition": rules[1].action,
                    "rule_id": rules[1].id,
                    "ruleset_id": ruleset.id,
                    "activation_instance_id": activation_instance.id,
                    "job_instance_id": None,
                },
            ],
            returning=[models.audit_rules],
        )
    ).all()

    await db.commit()

    return DBTestData(
        project,
        rulebook,
        ruleset,
        rules,
        inventory,
        activation_instance,
        audit_rules,
    )


async def test_list_rules(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    test_data = await _create_rules(db)
    project = test_data.project
    rulebook = test_data.rulebook
    ruleset = test_data.ruleset
    rules = test_data.rules

    response = await client.get("/api/rules")
    assert response.status_code == status_codes.HTTP_200_OK
    rule_list = response.json()
    assert isinstance(rule_list, list)
    assert len(rule_list) == len(rules)

    expected = {
        rule.id: {
            "id": rule.id,
            "name": rule.name,
            "ruleset": {
                "id": ruleset.id,
                "name": ruleset.name,
            },
            "rulebook": {
                "id": rulebook.id,
                "name": rulebook.name,
            },
            "project": {
                "id": project.id,
                "name": project.name,
            },
        }
        for rule in rules
    }
    for lst_rule in rule_list:
        exp_rule = expected[lst_rule["id"]]
        for exp_key in exp_rule:
            assert lst_rule[exp_key] == exp_rule[exp_key]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_read_rule(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    test_data = await _create_rules(db)
    project = test_data.project
    rulebook = test_data.rulebook
    ruleset = test_data.ruleset
    rules = test_data.rules

    response = await client.get(f"/api/rules/{rules[0].id}")
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    expected = {
        "id": rules[0].id,
        "name": rules[0].name,
        "action": rules[0].action,
        "ruleset": {
            "id": ruleset.id,
            "name": ruleset.name,
        },
        "rulebook": {
            "id": rulebook.id,
            "name": rulebook.name,
        },
        "project": {
            "id": project.id,
            "name": project.name,
        },
    }
    for exp_key in expected:
        assert expected[exp_key] == data[exp_key]

    assert len(data["fired_stats"]) > 0
    for fs in data["fired_stats"]:
        assert fs["total_type"] == "date_status_object"
        assert fs["object_status"] == "success"
        assert fs["date_status_total"] == 1
        assert fs["object_status_total"] == 1
        assert fs["pct_date_status_total"] == 100
        assert fs["window_total"] == 1
        assert fs["pct_window_total"] == 100

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_list_rulesets(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    test_data = await _create_rules(db)
    ruleset = test_data.ruleset
    rules = test_data.rules

    response = await client.get("/api/rulesets")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == [
        {
            "id": ruleset.id,
            "name": ruleset.name,
            "rule_count": len(rules),
            "created_at": ruleset.created_at.isoformat(),
            "modified_at": ruleset.created_at.isoformat(),
            "source_types": ["range"],
            "fired_stats": [
                {
                    "total_type": "status",
                    "status": "success",
                    "status_total": 2,
                    "object_total": 2,
                    "pct_object_total": 100,
                    "window_total": 2,
                    "pct_window_total": 100,
                }
            ],
        }
    ]

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_list_rulesets_no_stats(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    test_data = await _create_rules(db, (40, 41))
    ruleset = test_data.ruleset
    rules = test_data.rules

    response = await client.get("/api/rulesets")
    assert response.status_code == status_codes.HTTP_200_OK
    assert response.json() == [
        {
            "id": ruleset.id,
            "name": ruleset.name,
            "rule_count": len(rules),
            "created_at": ruleset.created_at.isoformat(),
            "modified_at": ruleset.created_at.isoformat(),
            "source_types": ["range"],
            "fired_stats": [],
        }
    ]


async def test_read_ruleset(
    client: AsyncClient, db: AsyncSession, check_permission_spy: mock.Mock
):
    test_data = await _create_rules(db)
    project = test_data.project
    rulebook = test_data.rulebook
    ruleset = test_data.ruleset
    rules = test_data.rules
    aud_rul = test_data.audit_rules

    expected = {
        "id": ruleset.id,
        "name": ruleset.name,
        "rule_count": len(rules),
        "created_at": ruleset.created_at.isoformat(),
        "modified_at": ruleset.modified_at.isoformat(),
        "sources": [
            {
                "name": "range",
                "type": "range",
                "source": "range",
                "config": {"limit": 5},
            }
        ],
        "rulebook": {
            "id": rulebook.id,
            "name": rulebook.name,
        },
        "project": {"id": project.id, "name": project.name},
    }

    response = await client.get(f"/api/rulesets/{ruleset.id}")
    assert response.status_code == status_codes.HTTP_200_OK

    respj = response.json()
    for key in expected:
        assert respj[key] == expected[key]

    assert len(respj["fired_stats"]) == 2
    for fs in respj["fired_stats"]:
        assert fs["total_type"] == "date_status_object"
        assert fs["fired_date"] in (
            str(aud_rul[0].fired_date.date()),
            str(aud_rul[1].fired_date.date()),
        )
        assert fs["object_status"] in (aud_rul[0].status, aud_rul[1].status)
        assert fs["object_status_total"] == 1
        assert fs["date_status_total"] == 1
        assert fs["pct_date_status_total"] == 100
        assert fs["window_total"] == 2
        assert fs["pct_window_total"] == 50

    check_permission_spy.assert_called_once_with(
        mock.ANY, mock.ANY, ResourceType.RULEBOOK, Action.READ
    )


async def test_read_ruleset_not_found(client: AsyncClient):
    response = await client.get("/api/rulesets/-1")
    assert response.status_code == status_codes.HTTP_404_NOT_FOUND


async def test_read_ruleset_rules(client: AsyncClient, db: AsyncSession):
    test_data = await _create_rules(db)
    ruleset = test_data.ruleset
    rules = test_data.rules

    response = await client.get(f"/api/rulesets/{ruleset.id}/rules")
    assert response.status_code == status_codes.HTTP_200_OK
    data = response.json()
    assert len(data) == len(rules)
    assert data[0]["id"] == rules[0].id
    assert data[0]["ruleset"]["id"] == ruleset.id
