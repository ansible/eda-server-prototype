import sqlalchemy as sa
from sqlalchemy import func

from .base import metadata

__all__ = (
    "activations",
    "activation_instances",
    "activation_instance_logs",
    "restart_policies",
)

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
        nullable=False,
    ),
    sa.Column(
        "restart_policy_id",
        sa.ForeignKey("restart_policy.id"),
        nullable=False,
    ),
    sa.Column(
        "playbook_id",
        sa.ForeignKey("playbook.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("status", sa.String),
    sa.Column("is_enabled", sa.Boolean, nullable=False),
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

restart_policies = sa.Table(
    "restart_policy",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String),
)


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
