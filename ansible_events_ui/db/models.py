import sqlalchemy
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

NAMING_CONVENTION = {
    # Index
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    # Unique constraint
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    # Check
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    # Foreign key
    "fk": "fk_%(table_name)s_%(column_0_N_name)s",
    # Primary key
    "pk": "pk_%(table_name)s",
}
metadata = sqlalchemy.MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


# TODO(cutwater): Rename into rulebooks
rulebooks = sqlalchemy.Table(
    "rulebook",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rulesets", sqlalchemy.String),
    sqlalchemy.Column(
        "project_id", sqlalchemy.ForeignKey("project.id"), nullable=True
    ),
)


rulesets = sqlalchemy.Table(
    "ruleset",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column(
        "rulebook_id",
        sqlalchemy.ForeignKey("rulebook.id"),
        nullable=False,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
)

rules = sqlalchemy.Table(
    "rule",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column(
        "ruleset_id",
        sqlalchemy.ForeignKey("ruleset.id"),
        nullable=False,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column(
        "action", postgresql.JSONB(none_as_null=True), nullable=False
    ),
)


inventories = sqlalchemy.Table(
    "inventory",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("inventory", sqlalchemy.String),
    sqlalchemy.Column(
        "project_id", sqlalchemy.ForeignKey("project.id"), nullable=True
    ),
)


extra_vars = sqlalchemy.Table(
    "extra_var",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("extra_var", sqlalchemy.String),
    sqlalchemy.Column(
        "project_id", sqlalchemy.ForeignKey("project.id"), nullable=True
    ),
)


activations = sqlalchemy.Table(
    "activation",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rulebook_id", sqlalchemy.ForeignKey("rulebook.id")),
    sqlalchemy.Column("inventory_id", sqlalchemy.ForeignKey("inventory.id")),
    sqlalchemy.Column("extra_var_id", sqlalchemy.ForeignKey("extra_var.id")),
)


activation_instances = sqlalchemy.Table(
    "activation_instance",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rulebook_id", sqlalchemy.ForeignKey("rulebook.id")),
    sqlalchemy.Column("inventory_id", sqlalchemy.ForeignKey("inventory.id")),
    sqlalchemy.Column("extra_var_id", sqlalchemy.ForeignKey("extra_var.id")),
)


activation_instance_logs = sqlalchemy.Table(
    "activation_instance_log",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column(
        "activation_instance_id",
        sqlalchemy.ForeignKey("activation_instance.id"),
    ),
    sqlalchemy.Column("line_number", sqlalchemy.Integer),
    sqlalchemy.Column("log", sqlalchemy.String),
)


projects = sqlalchemy.Table(
    "project",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("git_hash", sqlalchemy.String),
    sqlalchemy.Column("url", sqlalchemy.String),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    sqlalchemy.Column(
        "modified_at",
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)


jobs = sqlalchemy.Table(
    "job",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("uuid", postgresql.UUID),
)

job_instances = sqlalchemy.Table(
    "job_instance",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("uuid", postgresql.UUID),
)

activation_instance_job_instances = sqlalchemy.Table(
    "activation_instance_job_instance",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column(
        "activation_instance_id",
        sqlalchemy.ForeignKey("activation_instance.id"),
    ),
    sqlalchemy.Column(
        "job_instance_id", sqlalchemy.ForeignKey("job_instance.id")
    ),
)


job_instance_events = sqlalchemy.Table(
    "job_instance_event",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("job_uuid", postgresql.UUID),
    sqlalchemy.Column("counter", sqlalchemy.Integer),
    sqlalchemy.Column("stdout", sqlalchemy.String),
)


playbooks = sqlalchemy.Table(
    "playbook",
    metadata,
    sqlalchemy.Column(
        "id",
        sqlalchemy.Integer,
        sqlalchemy.Identity(always=True),
        primary_key=True,
    ),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("playbook", sqlalchemy.String),
    sqlalchemy.Column(
        "project_id", sqlalchemy.ForeignKey("project.id"), nullable=True
    ),
)


# FastAPI Users
class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
