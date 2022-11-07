from enum import Enum

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql

from .base import metadata

__all__ = (
    "activations",
    "activation_instances",
    "activation_instance_logs",
)


class RestartPolicy(str, Enum):
    ALWAYS = "always"
    ON_FAILURE = "on-failure"
    NEVER = "never"


activations = sa.Table(
    "activation",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String, nullable=False),
    sa.Column("description", sa.String),
    sa.Column("working_directory", sa.String),
    sa.Column("execution_environment", sa.String),
    sa.Column(
        "rulebook_id",
        sa.ForeignKey("rulebook.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "inventory_id",
        sa.ForeignKey("inventory.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column(
        "extra_var_id",
        sa.ForeignKey("extra_var.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "restart_policy",
        sa.Enum(
            RestartPolicy,
            name="restart_policy_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=RestartPolicy.ON_FAILURE,
        server_default=RestartPolicy.ON_FAILURE.value,
        nullable=False,
    ),
    sa.Column("status", sa.String),
    sa.Column(
        "is_enabled",
        sa.Boolean,
        nullable=False,
        default=True,
        server_default=sa.true(),
    ),
    sa.Column("restarted_at", sa.DateTime(timezone=True)),
    sa.Column("restart_count", sa.Integer, nullable=False, default=0),
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


# This table will have an pre-insert trigger that will
# set the large_data_id if it is null.
# This table will have a post-delete trigger that will
# cascade delete action to the large object table.
activation_instances = sa.Table(
    "activation_instance",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String),
    sa.Column("rulebook_id", sa.ForeignKey("rulebook.id", ondelete="CASCADE")),
    sa.Column(
        "inventory_id", sa.ForeignKey("inventory.id", ondelete="CASCADE")
    ),
    sa.Column(
        "extra_var_id", sa.ForeignKey("extra_var.id", ondelete="CASCADE")
    ),
    sa.Column("working_directory", sa.String),
    sa.Column("execution_environment", sa.String),
    sa.Column(
        "large_data_id",
        postgresql.OID,
        nullable=True,
        comment="OID of large object containing log(s).",
    ),
    sa.Column(
        "project_id",
        sa.ForeignKey("project.id", ondelete="CASCADE"),
        nullable=True,
    ),
)


activation_instance_logs = sa.Table(
    "activation_instance_log",
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
    sa.Column("line_number", sa.Integer),
    sa.Column("log", sa.String),
)
