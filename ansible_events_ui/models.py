import sqlalchemy
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.ext.declarative import declarative_base

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)


rule_set_files = sqlalchemy.Table(
    "rule_set_file",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rulesets", sqlalchemy.String),
)


inventories = sqlalchemy.Table(
    "inventory",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("inventory", sqlalchemy.String),
)


extra_vars = sqlalchemy.Table(
    "extra_var",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("extra_var", sqlalchemy.String),
)


activations = sqlalchemy.Table(
    "activation",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column(
        "rule_set_file_id", sqlalchemy.ForeignKey("rule_set_file.id")
    ),
    sqlalchemy.Column("inventory_id", sqlalchemy.ForeignKey("inventory.id")),
    sqlalchemy.Column("extra_var_id", sqlalchemy.ForeignKey("extra_var.id")),
)


activation_instances = sqlalchemy.Table(
    "activation_instance",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column(
        "rule_set_file_id", sqlalchemy.ForeignKey("rule_set_file.id")
    ),
    sqlalchemy.Column("inventory_id", sqlalchemy.ForeignKey("inventory.id")),
    sqlalchemy.Column("extra_var_id", sqlalchemy.ForeignKey("extra_var.id")),
    # sqlalchemy.Column(
    #     "activation_id", sqlalchemy.ForeignKey("activation.id")
    # ),
)


activation_instance_logs = sqlalchemy.Table(
    "activation_instance_log",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
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
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("git_hash", sqlalchemy.String),
    sqlalchemy.Column("url", sqlalchemy.String),
)


project_inventories = sqlalchemy.Table(
    "project_inventory",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey("project.id")),
    sqlalchemy.Column("inventory_id", sqlalchemy.ForeignKey("inventory.id")),
)

project_vars = sqlalchemy.Table(
    "project_var",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey("project.id")),
    sqlalchemy.Column("vars_id", sqlalchemy.ForeignKey("extra_var.id")),
)

project_rules = sqlalchemy.Table(
    "project_rule",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey("project.id")),
    sqlalchemy.Column(
        "rule_set_file_id", sqlalchemy.ForeignKey("rule_set_file.id")
    ),
)


jobs = sqlalchemy.Table(
    "job",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("uuid", sqlalchemy.String),
)

job_instances = sqlalchemy.Table(
    "job_instance",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("uuid", sqlalchemy.String),
    # sqlalchemy.Column("job_id", sqlalchemy.ForeignKey("job.id")),
)

activation_instance_job_instances = sqlalchemy.Table(
    "activation_instance_job_instance",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
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
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("job_uuid", sqlalchemy.String),
    sqlalchemy.Column("counter", sqlalchemy.Integer),
    sqlalchemy.Column("stdout", sqlalchemy.String),
)


playbooks = sqlalchemy.Table(
    "playbook",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("playbook", sqlalchemy.String),
)


project_playbooks = sqlalchemy.Table(
    "project_playbook",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey("project.id")),
    sqlalchemy.Column("playbook_id", sqlalchemy.ForeignKey("playbook.id")),
)


# FastAPI Users


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
