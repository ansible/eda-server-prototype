
import sqlalchemy
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID


metadata = sqlalchemy.MetaData()
Base: DeclarativeMeta = declarative_base()


rulesetfiles = sqlalchemy.Table(
    "rulesetfile",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rules", sqlalchemy.String),
)



inventories = sqlalchemy.Table(
    "inventory",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("inventory", sqlalchemy.String),
)



extravars = sqlalchemy.Table(
    "extravar",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("extravars", sqlalchemy.String),
)




activations = sqlalchemy.Table(
    "activation",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("rulesetfile_id", sqlalchemy.ForeignKey('rulesetfile.id')),
    sqlalchemy.Column("inventory_id", sqlalchemy.ForeignKey('inventory.id')),
    sqlalchemy.Column("extravars_id", sqlalchemy.ForeignKey('extravar.id')),
)


activation_logs = sqlalchemy.Table(
    "activation_log",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("activation_id", sqlalchemy.ForeignKey('activation.id')),
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


projectinventories = sqlalchemy.Table(
    "projectinventory",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey('project.id')),
    sqlalchemy.Column("inventory_id", sqlalchemy.ForeignKey('inventory.id')),
)

projectvars = sqlalchemy.Table(
    "projectvar",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey('project.id')),
    sqlalchemy.Column("vars_id", sqlalchemy.ForeignKey('extravar.id')),
)

projectrules = sqlalchemy.Table(
    "projectrule",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey('project.id')),
    sqlalchemy.Column("rules_id", sqlalchemy.ForeignKey('rulesetfile.id')),
)


jobs = sqlalchemy.Table(
    "job",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("uuid", sqlalchemy.String),
)

activationjobs = sqlalchemy.Table(
    "activationjob",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("activation_id", sqlalchemy.ForeignKey('activation.id')),
    sqlalchemy.Column("job_id", sqlalchemy.ForeignKey('job.id')),
)


job_events = sqlalchemy.Table(
    "job_event",
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


projectplaybooks = sqlalchemy.Table(
    "projectplaybook",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("project_id", sqlalchemy.ForeignKey('project.id')),
    sqlalchemy.Column("playbook_id", sqlalchemy.ForeignKey('playbook.id')),
)


# FastAPI Users 

class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
