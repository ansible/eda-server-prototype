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
from sqlalchemy.dialects import postgresql

from .base import metadata

__all__ = (
    "jobs",
    "job_instances",
    "job_instance_events",
    "job_instance_hosts",
    "activation_instance_job_instances",
)

jobs = sa.Table(
    "job",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("uuid", postgresql.UUID),
)

job_instances = sa.Table(
    "job_instance",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("uuid", postgresql.UUID),
    sa.Column("action", sa.String),
    sa.Column("name", sa.String),
    sa.Column("ruleset", sa.String),
    sa.Column("rule", sa.String),
    sa.Column("hosts", sa.String),
)

activation_instance_job_instances = sa.Table(
    "activation_instance_job_instance",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column(
        "activation_instance_id",
        sa.ForeignKey("activation_instance.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "job_instance_id", sa.ForeignKey("job_instance.id", ondelete="CASCADE")
    ),
)


job_instance_events = sa.Table(
    "job_instance_event",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("job_uuid", postgresql.UUID),
    sa.Column("counter", sa.Integer),
    sa.Column("stdout", sa.String),
    sa.Column("type", sa.String),
    sa.Column("created_at", sa.DateTime(timezone=True)),
)


job_instance_hosts = sa.Table(
    "job_instance_host",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("host", sa.String),
    sa.Column("job_uuid", postgresql.UUID),
    sa.Column("playbook", sa.String),
    sa.Column("play", sa.String),
    sa.Column("task", sa.String),
    sa.Column("status", sa.String),
)
