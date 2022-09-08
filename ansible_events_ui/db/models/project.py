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

from .mixins import IntIdMixin


class Project(IntIdMixin, Base):
    __tablename__ = "project"

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


class Inventory(IntIdMixin, Base):
    __tablename__ = "inventory"

    name = sa.Column(sa.String)
    inventory = sa.Column(sa.String)
    project_id = sa.Column(
        sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )


class ExtraVar(IntIdMixin, Base):
    __tablename__ = "extra_var"

    name = sa.Column(sa.String)
    extra_var = sa.Column(sa.String)
    project_id = sa.Column(
        sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )


class Playbook(IntIdMixin, Base):
    __tablename__ = "playbook"

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
