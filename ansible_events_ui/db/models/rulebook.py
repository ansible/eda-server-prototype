import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from .base import metadata

__all__ = (
    "rulebooks",
    "rulesets",
    "rules",
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
