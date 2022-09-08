import sqlalchemy as sa
from sqlalchemy import func

from .base import Base
from .mixins import IntIdMixin

__all__ = (
    "Activation",
    "ActivationInstance",
    "ActivationInstanceLog",
    "ExecutionEnvironment",
    "RestartPolicy",
    "activations",
    "activation_instances",
    "activation_instance_logs",
    "execution_envs",
    "restart_policies",
)


class Activation(IntIdMixin, Base):
    __tablename__ = "activation"
    id = sa.Column(sa.Integer, sa.Identity(always=True), primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    execution_env_id = sa.Column(
        sa.ForeignKey("execution_env.id", ondelete="CASCADE"), nullable=False
    )
    rulebook_id = sa.Column(
        sa.ForeignKey("rulebook.id", ondelete="CASCADE"), nullable=False
    )
    inventory_id = sa.Column(
        sa.ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    extra_var_id = sa.Column(
        sa.ForeignKey("extra_var.id", ondelete="CASCADE"), nullable=False
    )
    restart_policy_id = sa.Column(
        sa.ForeignKey("restart_policy.id"), nullable=False
    )
    playbook_id = sa.Column(
        sa.ForeignKey("playbook.id", ondelete="CASCADE"), nullable=False
    )
    activation_status = sa.Column(sa.String)
    activation_enabled = sa.Column(sa.Boolean, nullable=False)
    restarted_at = sa.Column(sa.DateTime(timezone=True))
    restarted_count = sa.Column(sa.Integer, nullable=False, default=0)
    created_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    modified_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ExecutionEnvironment(IntIdMixin, Base):
    __tablename__ = "execution_env"
    url = sa.Column(sa.String, nullable=False)


class RestartPolicy(IntIdMixin, Base):
    __tablename__ = "restart_policy"
    name = sa.Column(sa.String)


class ActivationInstance(IntIdMixin, Base):
    __tablename__ = "activation_instance"
    name = sa.Column(sa.String)
    rulebook_id = sa.Column(sa.ForeignKey("rulebook.id", ondelete="CASCADE"))
    inventory_id = sa.Column(sa.ForeignKey("inventory.id", ondelete="CASCADE"))
    extra_var_id = sa.Column(sa.ForeignKey("extra_var.id", ondelete="CASCADE"))


class ActivationInstanceLog(IntIdMixin, Base):
    __tablename__ = "activation_instance_log"
    activation_instance_id = sa.Column(
        sa.ForeignKey("activation_instance.id", ondelete="CASCADE")
    )
    line_number = sa.Column(sa.Integer)
    log = sa.Column(sa.String)


# TODO(cutwater): These tables are for compatibility with existing queries
#  only. They must be removed after queries are updated by using
#  declarative models.
activations = Activation.__table__
execution_envs = ExecutionEnvironment.__table__
restart_policies = RestartPolicy.__table__
activation_instances = ActivationInstance.__table__
activation_instance_logs = ActivationInstanceLog.__table__
