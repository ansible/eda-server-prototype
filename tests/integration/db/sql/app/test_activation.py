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
from typing import List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server.db import models
from eda_server.db.sql import base as bsql
from eda_server.db.sql.app import activation as asql
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
        "extra_var",
    ),
)


async def test_create_activation_instance(db: AsyncSession):
    test_data = await init_test_data(db)

    old_count = (
        await bsql.get_object(
            db,
            models.activation_instances,
            select_cols=[sa.func.count().label("count")],
        )
    ).count
    activation_data = await asql.create_activation_instance(
        db,
        {
            "name": "test-activation-instance",
            "rulebook_id": test_data.rulebooks[0].id,
            "inventory_id": test_data.inventory.id,
            "extra_var_id": test_data.extra_var.id,
            "working_directory": "/tmp",
            "execution_environment": "fedora:36",
            "project_id": test_data.project.id,
        },
    )
    new_count = (
        await bsql.get_object(
            db,
            models.activation_instances,
            select_cols=[sa.func.count().label("count")],
        )
    ).count

    cols = {
        "activation_instance_id",
        "activation_instance_large_data_id",
        "inventory",
        "rulesets",
        "ruleset_sources",
        "extra_var",
    }

    assert activation_data is not None
    assert activation_data.activation_instance_id is not None

    assert new_count > old_count
    assert isinstance(activation_data, sa.engine.Row)
    assert set(activation_data.keys()) == cols
    for col in cols:
        err_msg = f"Um, Column {col} is really not supposed to be None."
        assert activation_data[col] is not None, err_msg
    assert isinstance(activation_data.ruleset_sources, list)
    assert len(activation_data.ruleset_sources) > 0


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
            "rulesets": str({}),
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
                    "type": "websocket",
                    "config": {"port": 15000, "host": "client-ansible"},
                    "source": "test.client.websocket",
                }
            ],
        },
        {
            "rulebook_id": rulebook.id,
            "name": "ruleset-2",
            "sources": [
                {
                    "type": "websocket",
                    "config": {
                        "port": 15001,
                        "host": "client-replica-ansible",
                    },
                    "source": "test.client.other.websocket",
                }
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
        "inventory": '{"eek": {"ack": 1}}',
    }
    inventory = (
        await bsql.insert_object(
            db, models.inventories, values=vals, returning=[models.inventories]
        )
    ).one()

    return inventory


async def insert_extra_var(
    db: AsyncSession, project: sa.engine.Row
) -> sa.engine.Row:
    vals = {
        "name": "extra_var-1",
        "project_id": project.id,
        "extra_var": '{"limit": 1}',
    }
    extra_var = (
        await bsql.insert_object(
            db, models.extra_vars, values=vals, returning=[models.extra_vars]
        )
    ).one()

    return extra_var


async def init_test_data(db):
    project = await insert_project(db)
    rulebooks = await insert_rulebooks(db, project)
    rulesets = await insert_ruleset(db, rulebooks[0])
    rules = await insert_rule(db, rulesets)
    inventory = await insert_inventory(db, project)
    extra_var = await insert_extra_var(db, project)

    return DBTestData(
        project,
        rulebooks,
        rulesets,
        rules,
        inventory,
        extra_var,
    )
