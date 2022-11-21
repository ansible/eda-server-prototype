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

import os
from collections import namedtuple
from datetime import datetime, timezone
from typing import List

import sqlalchemy as sa
import yaml
from dateutil.parser import parse as dtparse
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import project as bl_prj
from eda_server.db import models
from eda_server.db.sql import base as bsql, rulebook as rsql
from eda_server.types import InventorySource

TEST_RULESET_SIMPLE = """
---
- name: Test simple
  hosts: all
  sources:
    - name: range
      range:
        limit: 5
    - kafka:
        port: 9092
        topic: test_rulebook

  rules:
    - name: Test simple rule 1
      condition: event.i == 1
      action:
        debug:
"""


DBTestData = namedtuple(
    "DBTestData",
    (
        "project",
        "rulebooks",
        "rulesets",
        "rules",
        "inventory",
        "activation_instances",
        "audit_rules",
    ),
)


MIN_FIRED_DATE = datetime(2022, 9, 28, 20, 21, 57, 672699, tzinfo=timezone.utc)
MAX_FIRED_DATE = datetime(2022, 10, 4, 22, 21, 57, 672699, tzinfo=timezone.utc)


def test_build_ruleset_fire_count_query():
    query = rsql.build_object_fire_counts_query(rsql.AuditGrouping.RULESET)
    query_str = str(query).lower().replace(os.linesep, " ")
    assert isinstance(query, sa.sql.Select)
    assert " a_ar.ruleset_id" in query_str
    assert " grouping sets" in query_str


def test_build_rule_fire_count_query():
    query = rsql.build_object_fire_counts_query(rsql.AuditGrouping.RULE)
    query_str = str(query).lower().replace(os.linesep, " ")
    assert isinstance(query, sa.sql.Select)
    assert " a_ar.rule_id" in query_str
    assert " grouping sets" in query_str


def test_build_ruleset_id_fire_count_query():
    query = rsql.build_object_fire_counts_query(
        rsql.AuditGrouping.RULESET, object_id=1
    )
    query_str = str(query).lower().replace(os.linesep, " ")
    assert " a_ar.ruleset_id" in query_str
    assert " grouping sets" in query_str
    assert " a_ar.ruleset_id = :ruleset_id_1" in query_str


async def test_get_fire_counts_data(db: AsyncSession):
    await init_test_data(db)
    res = (
        await rsql.get_fired_counts(
            db,
            rsql.AuditGrouping.RULESET,
            window_start=MIN_FIRED_DATE,
            window_end=MAX_FIRED_DATE,
        )
    ).all()
    ruleset_ids = {rec.ruleset_id for rec in res}
    assert len(ruleset_ids) > 1
    row_types = {rec.row_type[2:] for rec in res}
    expected = {
        rsql.WINDOW_TOTAL,
        rsql.DATE_TOTAL,
        rsql.STATUS_TOTAL,
        rsql.OBJECT_TOTAL,
        rsql.DATE_STATUS_TOTAL,
        rsql.DATE_OBJECT_TOTAL,
        rsql.STATUS_OBJECT_TOTAL,
        rsql.DATE_STATUS_OBJECT_TOTAL,
    }
    assert row_types == expected
    assert res[0].row_type[2:] == rsql.WINDOW_TOTAL


async def test_get_ruleset_fire_counts_data(db: AsyncSession):
    test_data = await init_test_data(db)
    cur = await rsql.get_fired_counts(
        db,
        rsql.AuditGrouping.RULESET,
        test_data.audit_rules[0].ruleset_id,
        window_start=MIN_FIRED_DATE,
        window_end=MAX_FIRED_DATE,
    )
    res = cur.all()
    ruleset_ids = {rec.ruleset_id for rec in res if rec.ruleset_id is not None}
    assert len(ruleset_ids) == 1
    row_types = {rec.row_type[2:] for rec in res}
    assert len(row_types) > 1
    expected = {
        rsql.WINDOW_TOTAL,
        rsql.DATE_TOTAL,
        rsql.STATUS_TOTAL,
        rsql.OBJECT_TOTAL,
        rsql.DATE_STATUS_TOTAL,
        rsql.DATE_OBJECT_TOTAL,
        rsql.STATUS_OBJECT_TOTAL,
        rsql.DATE_STATUS_OBJECT_TOTAL,
    }
    assert row_types == expected
    assert res[0].row_type[2:] == rsql.WINDOW_TOTAL


async def test_index_fire_counts_data(db: AsyncSession):
    await init_test_data(db)
    res = (
        await rsql.get_fired_counts(
            db,
            rsql.AuditGrouping.RULESET,
            window_start=MIN_FIRED_DATE,
            window_end=MAX_FIRED_DATE,
        )
    ).all()
    idx_res = await rsql.index_grouped_objects(res, rsql.AuditGrouping.RULESET)
    assert isinstance(idx_res, dict)
    expected = {
        rsql.WINDOW_TOTAL,
        rsql.DATE_TOTAL,
        rsql.STATUS_TOTAL,
        rsql.OBJECT_TOTAL,
        rsql.DATE_STATUS_TOTAL,
        rsql.DATE_OBJECT_TOTAL,
        rsql.STATUS_OBJECT_TOTAL,
        rsql.DATE_STATUS_OBJECT_TOTAL,
    }
    assert set(idx_res) == expected


async def test_get_indexed_fire_counts_data(db: AsyncSession):
    await init_test_data(db)
    res = await rsql.get_indexed_fired_counts(
        db,
        rsql.AuditGrouping.RULESET,
        window_start=MIN_FIRED_DATE,
        window_end=MAX_FIRED_DATE,
    )
    assert isinstance(res, dict)
    expected = {
        rsql.WINDOW_TOTAL,
        rsql.DATE_TOTAL,
        rsql.STATUS_TOTAL,
        rsql.OBJECT_TOTAL,
        rsql.DATE_STATUS_TOTAL,
        rsql.DATE_OBJECT_TOTAL,
        rsql.STATUS_OBJECT_TOTAL,
        rsql.DATE_STATUS_OBJECT_TOTAL,
    }
    assert set(res) == expected


def test_build_ruleset_base_query():
    query = rsql.build_ruleset_base_query()
    query_str = str(query).lower().replace(os.linesep, " ")
    assert isinstance(query, sa.sql.Select)
    assert " a_rs.id" in query_str
    assert " rule_count" in query_str
    assert " as rulebook" in query_str
    assert " as project" in query_str


async def test_get_ruleset_base_data(db: AsyncSession):
    test_data = await init_test_data(db)
    query = rsql.build_ruleset_base_query(test_data.rulesets[0].id)
    res = await bsql.execute_get_result(db, query)
    assert len(res) > 1
    assert len(res.sources) > 0
    assert res.rule_count > 0
    assert res.rulebook["id"] == test_data.rulebooks[0].id
    assert res.project["id"] == test_data.project.id


async def test_get_ruleset_base_no_data(db: AsyncSession):
    await init_test_data(db)
    query = rsql.build_ruleset_base_query(-1)
    res = await bsql.execute_get_result(db, query)
    assert res is None


async def test_get_rulesets_base_no_data(db: AsyncSession):
    query = rsql.build_ruleset_base_query()
    res = await bsql.execute_get_result(db, query)
    assert res is None


async def test_expand_ruleset_sources(db: AsyncSession):
    rulesets_data = yaml.safe_load(TEST_RULESET_SIMPLE)
    res = bl_prj.expand_ruleset_sources(rulesets_data)
    rs_name = "Test simple"
    assert rs_name in res
    assert len(res[rs_name]) == 2
    for xp_src in res[rs_name]:
        assert {"type", "source", "config", "name"} == set(xp_src)
        assert isinstance(xp_src["config"], dict)
        if xp_src["type"] == "kafka":
            assert xp_src["name"] == "<unnamed>"
        else:
            assert xp_src["name"] != "<unnamed>"


async def test_process_ruleset_sources(db: AsyncSession):
    project = await insert_project(db)
    rulebooks = await insert_rulebooks(db, project)
    assert len(rulebooks) == 2
    rulebook_data = yaml.safe_load(rulebooks[1].rulesets)
    await bl_prj.insert_rulebook_related_data(
        db, rulebooks[1].id, rulebook_data
    )
    ruleset = await bsql.get_object(
        db,
        models.rulesets,
        filters=models.rulesets.c.rulebook_id == rulebooks[1].id,
    )
    assert ruleset is not None
    assert ruleset.name == "Test simple"
    assert len(ruleset.sources) == 2
    rule = await bsql.get_object(
        db, models.rules, filters=models.rules.c.ruleset_id == ruleset.id
    )
    assert rule is not None
    assert rule.name == "Test simple rule 1"


# -------------------------------------------------------------------------
#  Test Data
# -------------------------------------------------------------------------


async def insert_project(db: AsyncSession) -> sa.engine.Row:
    vals = {
        "git_hash": "",
        "url": "",
        "name": "proj-1",
        "description": "",
    }
    project = (
        await bsql.insert_object(
            db, models.projects, values=vals, returning=[models.projects]
        )
    ).one()

    return project


async def insert_rulebooks(
    db: AsyncSession, project: sa.engine.Row
) -> sa.engine.Row:
    vals = [
        {
            "name": "rulebook-1",
            "project_id": project.id,
            "rulesets": None,
        },
        {
            "name": "rulebook-2",
            "project_id": project.id,
            "rulesets": TEST_RULESET_SIMPLE,
        },
    ]
    rulebooks = (
        await bsql.insert_object(
            db, models.rulebooks, values=vals, returning=[models.rulebooks]
        )
    ).all()

    return rulebooks


async def insert_ruleset(
    db: AsyncSession, rulebook: sa.engine.Row
) -> sa.engine.Row:
    vals = [
        {
            "rulebook_id": rulebook.id,
            "name": "ruleset-1",
            "sources": [
                {
                    "type": "amqp",
                    "config": {"port": 433},
                    "source": "example.ansible.amqp",
                }
            ],
        },
        {
            "rulebook_id": rulebook.id,
            "name": "ruleset-2",
            "sources": [
                {
                    "type": "webhook",
                    "config": {
                        "url": "https://api.example.com/v1/action-hook"
                    },
                    "source": "example.ansible.webhook",
                }
            ],
        },
        {
            "rulebook_id": rulebook.id,
            "name": "ruleset-63",
            "sources": [
                {
                    "type": "webhook",
                    "config": {
                        "url": "https://api.example.com/v1/action-hook"
                    },
                    "source": "example.ansible.webhook",
                },
                {
                    "type": "sensor",
                    "config": {"interrupt": "0xA235"},
                    "source": "example.sensor",
                },
            ],
        },
    ]
    rulesets = (
        await bsql.insert_object(
            db, models.rulesets, values=vals, returning=[models.rulesets]
        )
    ).all()

    return rulesets


async def insert_rule(
    db: AsyncSession, rulesets: List[sa.engine.Row]
) -> sa.engine.Row:
    vals = [
        {"ruleset_id": rulesets[0].id, "name": "rule-1", "action": {}},
        {"ruleset_id": rulesets[1].id, "name": "rule-2", "action": {}},
        {"ruleset_id": rulesets[2].id, "name": "rule-23", "action": {}},
        {"ruleset_id": rulesets[0].id, "name": "rule-11", "action": {}},
        {"ruleset_id": rulesets[0].id, "name": "rule-12", "action": {}},
        {"ruleset_id": rulesets[0].id, "name": "rule-13", "action": {}},
        {"ruleset_id": rulesets[0].id, "name": "rule-14", "action": {}},
        {"ruleset_id": rulesets[0].id, "name": "rule-15", "action": {}},
    ]
    rules = (
        await bsql.insert_object(
            db, models.rules, values=vals, returning=[models.rules]
        )
    ).all()

    return rules


async def insert_inventory(
    db: AsyncSession, project: sa.engine.Row
) -> sa.engine.Row:
    vals = {
        "name": "inventory-1",
        "project_id": project.id,
        "inventory_source": InventorySource.PROJECT,
    }
    inventory = (
        await bsql.insert_object(
            db, models.inventories, values=vals, returning=[models.inventories]
        )
    ).one()

    return inventory


async def insert_activation_instance(
    db: AsyncSession,
    rulebook: sa.engine.Row,
    inventory: sa.engine.Row,
) -> List[sa.engine.Row]:
    vals = [
        {
            "name": "act-inst-1",
            "rulebook_id": rulebook.id,
            "inventory_id": inventory.id,
        },
        {
            "name": "act-inst-2",
            "rulebook_id": rulebook.id,
            "inventory_id": inventory.id,
        },
        {
            "name": "act-inst-3",
            "rulebook_id": rulebook.id,
            "inventory_id": inventory.id,
        },
        {
            "name": "act-inst-4",
            "rulebook_id": rulebook.id,
            "inventory_id": inventory.id,
        },
    ]
    activation_instance = (
        await bsql.insert_object(
            db,
            models.activation_instances,
            values=vals,
            returning=[models.activation_instances],
        )
    ).all()

    return activation_instance


async def insert_audit_rule(
    db: AsyncSession,
    rulesets: List[sa.engine.Row],
    rules: List[sa.engine.Row],
    activation_instances: List[sa.engine.Row],
) -> List[sa.engine.Row]:
    vals = [
        {
            "name": "rule-1",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-10-02T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[0].id,
            "ruleset_id": rulesets[0].id,
            "activation_instance_id": activation_instances[0].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-1",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-10-03T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[0].id,
            "ruleset_id": rulesets[0].id,
            "activation_instance_id": activation_instances[0].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-1",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-10-03T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[0].id,
            "ruleset_id": rulesets[0].id,
            "activation_instance_id": activation_instances[1].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-2",
            "description": "",
            "status": "fail",
            "fired_date": dtparse("2022-10-04T19:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[1].id,
            "ruleset_id": rulesets[1].id,
            "activation_instance_id": activation_instances[2].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-2",
            "description": "",
            "status": "fail",
            "fired_date": dtparse("2022-10-04T19:51:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[1].id,
            "ruleset_id": rulesets[1].id,
            "activation_instance_id": activation_instances[2].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-2",
            "description": "",
            "status": "running",
            "fired_date": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[1].id,
            "ruleset_id": rulesets[1].id,
            "activation_instance_id": activation_instances[2].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-10",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-09-28T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[2].id,
            "ruleset_id": rulesets[2].id,
            "activation_instance_id": activation_instances[3].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-10",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-09-29T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[2].id,
            "ruleset_id": rulesets[2].id,
            "activation_instance_id": activation_instances[3].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-10",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-09-30T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[2].id,
            "ruleset_id": rulesets[2].id,
            "activation_instance_id": activation_instances[3].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-10",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-10-01T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[2].id,
            "ruleset_id": rulesets[2].id,
            "activation_instance_id": activation_instances[3].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-10",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-10-02T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[2].id,
            "ruleset_id": rulesets[2].id,
            "activation_instance_id": activation_instances[3].id,
            "job_instance_id": None,
        },
        {
            "name": "rule-10",
            "description": "",
            "status": "success",
            "fired_date": dtparse("2022-10-03T20:21:57.672699+00:00"),
            "created_at": dtparse("2022-10-04T20:21:57.672699+00:00"),
            "definition": {},
            "rule_id": rules[2].id,
            "ruleset_id": rulesets[2].id,
            "activation_instance_id": activation_instances[3].id,
            "job_instance_id": None,
        },
    ]
    rules = (
        await bsql.insert_object(
            db, models.audit_rules, values=vals, returning=[models.audit_rules]
        )
    ).all()

    return rules


async def init_test_data(db):
    project = await insert_project(db)
    rulebooks = await insert_rulebooks(db, project)
    rulesets = await insert_ruleset(db, rulebooks[0])
    rules = await insert_rule(db, rulesets)
    inventory = await insert_inventory(db, project)
    activation_instances = await insert_activation_instance(
        db, rulebooks[0], inventory
    )
    audit_rules = await insert_audit_rule(
        db, rulesets, rules, activation_instances
    )

    return DBTestData(
        project,
        rulebooks,
        rulesets,
        rules,
        inventory,
        activation_instances,
        audit_rules,
    )
