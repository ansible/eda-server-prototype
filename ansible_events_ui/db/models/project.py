import sqlalchemy as sa

from .base import metadata

__all__ = (
    "projects",
    "inventories",
    "extra_vars",
    "playbooks",
)

projects = sa.Table(
    "project",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("git_hash", sa.String),
    sa.Column("url", sa.String),
)

inventories = sa.Table(
    "inventory",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String),
    sa.Column("inventory", sa.String),
    sa.Column("project_id", sa.ForeignKey("project.id"), nullable=True),
)


extra_vars = sa.Table(
    "extra_var",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String),
    sa.Column("extra_var", sa.String),
    sa.Column("project_id", sa.ForeignKey("project.id"), nullable=True),
)

playbooks = sa.Table(
    "playbook",
    metadata,
    sa.Column(
        "id",
        sa.Integer,
        sa.Identity(always=True),
        primary_key=True,
    ),
    sa.Column("name", sa.String),
    sa.Column("playbook", sa.String),
    sa.Column("project_id", sa.ForeignKey("project.id"), nullable=True),
)
