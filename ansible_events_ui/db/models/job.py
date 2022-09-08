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

from .mixins import IntIdMixin


class Job(IntIdMixin, Base):
    __tablename__ = "job"

    uuid = sa.Column(postgresql.UUID)


class JobInstance(IntIdMixin, Base):
    __tablename__ = "job_instance"

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


class JobInstanceEvent(IntIdMixin, Base):
    __tablename__ = "job_instance_event"

    job_uuid = sa.Column(postgresql.UUID)
    counter = sa.Column(sa.Integer)
    stdout = sa.Column(sa.String)


# TODO(cutwater): These tables are for compatibility with existing queries
#  only. They must be removed after queries are updated by using
#  declarative models.
jobs = Job.__table__
job_instances = JobInstance.__table__
job_instance_events = JobInstanceEvent.__table__
