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

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql

from .base import metadata

__all__ = (
    "rulebooks",
    "rulesets",
    "rules",
    "audit_rules",
)

rulebooks = sa.Table(
    "rulebook",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String),
    sa.Column("description", sa.String),
    sa.Column("rulesets", sa.String),
    sa.Column(
        "project_id",
        sa.ForeignKey("project.id", ondelete="CASCADE"),
        nullable=True,
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    sa.Column(
        "modified_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)


rulesets = sa.Table(
    "ruleset",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column(
        "rulebook_id",
        sa.ForeignKey("rulebook.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("name", sa.String),
    sa.Column(
        "sources",
        postgresql.JSONB(none_as_null=True),
        comment="Expanded source information from ruleset data.",
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    sa.Column(
        "modified_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)

rules = sa.Table(
    "rule",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column(
        "ruleset_id",
        sa.ForeignKey("ruleset.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("name", sa.String),
    sa.Column("action", postgresql.JSONB(none_as_null=True), nullable=False),
)

audit_rules = sa.Table(
    "audit_rule",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String),
    sa.Column("description", sa.String),
    sa.Column("status", sa.String),
    sa.Column(
        "fired_date", sa.DateTime(timezone=True), server_default=func.now()
    ),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    sa.Column(
        "definition", postgresql.JSONB(none_as_null=True), nullable=False
    ),
    sa.Column(
        "rule_id",
        sa.ForeignKey("rule.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "ruleset_id",
        sa.ForeignKey("ruleset.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "activation_instance_id",
        sa.ForeignKey("activation_instance.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "job_instance_id",
        sa.ForeignKey("job_instance.id", ondelete="CASCADE"),
    ),
)
