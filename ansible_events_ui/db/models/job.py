import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from .base import metadata

__all__ = (
    "jobs",
    "job_instances",
    "job_instance_events",
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
