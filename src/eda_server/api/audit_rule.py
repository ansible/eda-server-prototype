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

from typing import List

import sqlalchemy as sa
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from eda_server import schema
from eda_server.auth import requires_permission
from eda_server.db import models
from eda_server.db.dependency import get_db_session
from eda_server.types import Action, ResourceType

router = APIRouter(tags=["audit_rules"])


@router.get(
    "/api/audit/rule/{rule_id}/details",
    response_model=schema.AuditRule,
    operation_id="read_audit_rule_details",
    dependencies=[
        Depends(requires_permission(ResourceType.AUDIT_RULE, Action.READ)),
    ],
)
async def read_audit_rule_details(
    rule_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.audit_rules.c.name,
            models.audit_rules.c.description,
            models.audit_rules.c.status,
            models.audit_rules.c.ruleset_id,
            models.rulesets.c.name.label("ruleset_name"),
            models.audit_rules.c.activation_instance_id,
            models.activation_instances.c.name.label(
                "activation_instance_name"
            ),
            models.audit_rules.c.created_at,
            models.audit_rules.c.fired_date,
            models.audit_rules.c.definition,
        )
        .select_from(
            models.audit_rules.join(models.rulesets).join(
                models.activation_instances
            )
        )
        .filter(models.audit_rules.c.id == rule_id)
    )
    row = (await db.execute(query)).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {
        "name": row["name"],
        "description": row["description"],
        "status": row["status"],
        "activation": {
            "id": row["activation_instance_id"],
            "name": row["activation_instance_name"],
        },
        "ruleset": {
            "id": row["ruleset_id"],
            "name": row["ruleset_name"],
        },
        "created_at": row["created_at"],
        "fired_date": row["fired_date"],
        "definition": row["definition"],
    }


@router.get(
    "/api/audit/rule/{rule_id}/jobs",
    response_model=List[schema.AuditRuleJobInstance],
    operation_id="list_audit_rule_jobs",
    dependencies=[
        Depends(requires_permission(ResourceType.AUDIT_RULE, Action.READ)),
    ],
)
async def list_audit_rule_jobs(
    rule_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.audit_rules.c.id,
            models.audit_rules.c.job_instance_id,
            models.audit_rules.c.status,
            models.audit_rules.c.fired_date,
        )
        .select_from(models.audit_rules)
        .filter(models.audit_rules.c.id == rule_id)
    )
    rows = (await db.execute(query)).all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response = []
    for row in rows:
        response.append(
            {
                "id": row["job_instance_id"],
                "status": row["status"],
                "last_fired_date": row["fired_date"],
            }
        )
    return response


@router.get(
    "/api/audit/rule/{rule_id}/hosts",
    response_model=List[schema.AuditRuleHost],
    operation_id="list_audit_rule_hosts",
    dependencies=[
        Depends(requires_permission(ResourceType.AUDIT_RULE, Action.READ)),
    ],
)
async def list_audit_rule_hosts(
    rule_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.audit_rules.c.id,
            models.audit_rules.c.job_instance_id,
            models.job_instances.c.uuid,
            models.job_instance_hosts.c.id.label("host_id"),
            models.job_instance_hosts.c.status,
            models.job_instance_hosts.c.host,
        )
        .select_from(models.audit_rules)
        .join(
            models.job_instances,
            models.audit_rules.c.job_instance_id == models.job_instances.c.id,
        )
        .join(
            models.job_instance_hosts,
            models.job_instances.c.uuid
            == models.job_instance_hosts.c.job_uuid,
        )
        .filter(models.audit_rules.c.id == rule_id)
    )
    rows = (await db.execute(query)).all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    response = []
    for row in rows:
        response.append(
            {
                "id": row["host_id"],
                "name": row["host"],
                "status": row["status"],
            }
        )
    return response


@router.get(
    "/api/audit/rule/{rule_id}/events",
    response_model=List[schema.AuditRuleJobInstanceEvent],
    operation_id="list_audit_rule_events",
    dependencies=[
        Depends(requires_permission(ResourceType.AUDIT_RULE, Action.READ)),
    ],
)
async def list_audit_rule_events(
    rule_id: int, db: AsyncSession = Depends(get_db_session)
):
    query = (
        sa.select(
            models.audit_rules.c.job_instance_id,
            models.audit_rules.c.name,
            models.job_instances.c.uuid,
            models.job_instance_events.c.id,
            models.job_instance_events.c.counter,
            models.job_instance_events.c.type,
            models.job_instance_events.c.created_at,
        )
        .select_from(models.audit_rules)
        .join(
            models.job_instances,
            models.job_instances.c.id == models.audit_rules.c.job_instance_id,
        )
        .join(
            models.job_instance_events,
            models.job_instance_events.c.job_uuid
            == models.job_instances.c.uuid,
        )
        .filter(models.audit_rules.c.id == rule_id)
    )
    rows = (await db.execute(query)).all()
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    response = []
    for row in rows:
        response.append(
            {
                "id": row["job_instance_event_id"],
                "name": row["name"],
                "increment_counter": row["job_instance_event_counter"],
                "type": row["type"],
                "timestamp": row["created_at"],
            }
        )
    return response


@router.get(
    "/api/audit/rules_fired",
    response_model=List[schema.AuditFiredRule],
    operation_id="list_audit_rules_fired",
    dependencies=[
        Depends(requires_permission(ResourceType.AUDIT_RULE, Action.READ)),
    ],
)
async def list_audit_rules_fired(db: AsyncSession = Depends(get_db_session)):
    query = (
        sa.select(
            models.audit_rules.c.rule_id.label("rule_id"),
            models.audit_rules.c.name.label("rule_name"),
            models.audit_rules.c.job_instance_id.label("job_id"),
            models.job_instance_hosts.c.task.label("job_name"),
            models.audit_rules.c.status.label("status"),
            models.rulesets.c.id.label("ruleset_id"),
            models.rulesets.c.name.label("ruleset_name"),
            models.audit_rules.c.fired_date.label("fired_date"),
        )
        .select_from(
            models.audit_rules.join(
                models.rulesets,
                models.rulesets.c.id == models.audit_rules.c.ruleset_id,
            )
            .join(
                models.job_instances,
                models.audit_rules.c.job_instance_id
                == models.job_instances.c.id,
            )
            .join(
                models.job_instance_hosts,
                models.job_instance_hosts.c.job_uuid
                == models.job_instances.c.uuid,
            )
        )
        .order_by(desc(models.audit_rules.c.fired_date))
    )

    response = []

    rows = (await db.execute(query)).all()
    for row in rows:
        response.append(
            {
                "job": {
                    "id": row["job_id"],
                    "name": row["job_name"],
                },
                "status": row["status"],
                "fired_date": row["fired_date"],
                "rule": {
                    "id": row["rule_id"],
                    "name": row["rule_name"],
                },
                "ruleset": {
                    "id": row["ruleset_id"],
                    "name": row["ruleset_name"],
                },
            }
        )

    return response


@router.get(
    "/api/audit/hosts_changed",
    response_model=List[schema.AuditChangedHost],
    operation_id="list_audit_hosts_changed",
    dependencies=[
        Depends(requires_permission(ResourceType.AUDIT_RULE, Action.READ)),
    ],
)
async def list_audit_hosts_changed(db: AsyncSession = Depends(get_db_session)):
    query = (
        sa.select(
            models.job_instance_hosts.c.host.label("host"),
            models.audit_rules.c.rule_id.label("rule_id"),
            models.audit_rules.c.name.label("rule_name"),
            models.rulesets.c.id.label("ruleset_id"),
            models.rulesets.c.name.label("ruleset_name"),
            models.audit_rules.c.fired_date.label("fired_date"),
        )
        .select_from(
            models.audit_rules.join(
                models.rulesets,
                models.rulesets.c.id == models.audit_rules.c.ruleset_id,
            )
            .join(
                models.job_instances,
                models.audit_rules.c.job_instance_id
                == models.job_instances.c.id,
            )
            .join(
                models.job_instance_hosts,
                models.job_instance_hosts.c.job_uuid
                == models.job_instances.c.uuid,
            )
        )
        .order_by(desc(models.audit_rules.c.fired_date))
    )

    response = []

    rows = (await db.execute(query)).all()
    for row in rows:
        response.append(
            {
                "host": row["host"],
                "fired_date": row["fired_date"],
                "rule": {
                    "id": row["rule_id"],
                    "name": row["rule_name"],
                },
                "ruleset": {
                    "id": row["ruleset_id"],
                    "name": row["ruleset_name"],
                },
            }
        )

    return response
