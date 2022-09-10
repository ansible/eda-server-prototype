import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from .base import Base

__all__ = (
    "jobs",
    "job_instances",
    "job_instance_events",
    "activation_instance_job_instances",
    "Job",
    "JobInstance",
    "JobInstanceEvent",
)


class Job(Base):
    __tablename__ = "job"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    uuid = sa.Column(postgresql.UUID)


class JobInstance(Base):
    __tablename__ = "job_instance"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    uuid = sa.Column(postgresql.UUID)


activation_instance_job_instances = sa.Table(
    "activation_instance_job_instance",
    Base.metadata,
    sa.Column("id", sa.Integer, sa.Identity(always=True), primary_key=True),
    sa.Column(
        "activation_instance_id",
        sa.ForeignKey("activation_instance.id", ondelete="CASCADE"),
    ),
    sa.Column(
        "job_instance_id", sa.ForeignKey("job_instance.id", ondelete="CASCADE")
    ),
)


class JobInstanceEvent(Base):
    __tablename__ = "job_instance_event"

    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    job_uuid = sa.Column(postgresql.UUID)
    counter = sa.Column(sa.Integer)
    stdout = sa.Column(sa.String)


# TODO(cutwater): These tables are for compatibility with existing queries
#  only. They must be removed after queries are updated by using
#  declarative models.
jobs = Job.__table__
job_instances = JobInstance.__table__
job_instance_events = JobInstanceEvent.__table__
