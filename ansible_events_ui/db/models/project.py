import sqlalchemy as sa
from sqlalchemy import func

from .base import Base

__all__ = (
    "projects",
    "inventories",
    "extra_vars",
    "playbooks",
    "Project",
    "Inventory",
    "ExtraVar",
    "Playbook",
)


class Project(Base):
    __tablename__ = "project"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    git_hash = sa.Column(sa.String)
    url = sa.Column(sa.String)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    modified_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    name = sa.Column(sa.String)
    inventory = sa.Column(sa.String)
    project_id = sa.Column(
        sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )


class ExtraVar(Base):
    __tablename__ = "extra_var"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    name = sa.Column(sa.String)
    extra_var = sa.Column(sa.String)
    project_id = sa.Column(
        sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )


class Playbook(Base):
    __tablename__ = "playbook"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    name = sa.Column(sa.String)
    playbook = sa.Column(sa.String)
    project_id = sa.Column(
        sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )


# TODO(cutwater): These tables are for compatibility with existing queries
#  only. They must be removed after queries are updated by using
#  declarative models.
projects = Project.__table__
inventories = Inventory.__table__
extra_vars = ExtraVar.__table__
playbooks = Playbook.__table__
