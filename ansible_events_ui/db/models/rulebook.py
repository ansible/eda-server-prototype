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
    sa.Column("rulesets", sa.String),
    sa.Column(
        "project_id",
        sa.ForeignKey("project.id", ondelete="CASCADE"),
        nullable=True,
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
        sa.ForeignKey("rule.id"),
        nullable=False,
    ),
    sa.Column(
        "ruleset_id",
        sa.ForeignKey("ruleset.id"),
        nullable=False,
    ),
    sa.Column(
        "activation_instance_id",
        sa.ForeignKey("activation_instance.id"),
        nullable=False,
    ),
    sa.Column(
        "job_instance_id",
        sa.ForeignKey("job_instance.id"),
    ),
)
