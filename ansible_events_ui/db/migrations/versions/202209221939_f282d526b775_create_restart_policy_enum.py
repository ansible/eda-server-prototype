"""Create enum tables for restart policy and execution environment.

Revision ID: f282d526b775
Revises: d4df045eb3ce
Create Date: 2022-09-22 19:39:23.365448+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f282d526b775"
down_revision = "d4df045eb3ce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    restart_policy = sa.Enum(
        "always", "on-failure", "never", name="restart_policy_enum"
    )
    restart_policy.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "activation",
        sa.Column(
            "restart_policy",
            restart_policy,
            server_default="on-failure",
            nullable=False,
        ),
    )
    execution_environment = sa.Enum(
        "docker", "podman", "k8s", "local", name="execution_environment_enum"
    )
    execution_environment.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "activation",
        "execution_environment",
        type_=execution_environment,
        postgresql_using="execution_environment::execution_environment_enum",
        server_default="docker",
        nullable=False,
    )
    op.alter_column(
        "activation", "extra_var_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column("activation", "is_enabled", server_default=sa.true())
    op.drop_constraint(
        "fk_activation_playbook_id", "activation", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_activation_restart_policy_id", "activation", type_="foreignkey"
    )
    op.drop_column("activation", "restart_policy_id")
    op.drop_column("activation", "playbook_id")
    op.drop_table("restart_policy")


def downgrade() -> None:
    op.create_table(
        "restart_policy",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(
                always=True,
                start=1,
                increment=1,
                minvalue=1,
                maxvalue=2147483647,
                cycle=False,
                cache=1,
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_restart_policy"),
    )
    op.add_column(
        "activation",
        sa.Column(
            "playbook_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "activation",
        sa.Column(
            "restart_policy_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_activation_restart_policy_id",
        "activation",
        "restart_policy",
        ["restart_policy_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_playbook_id",
        "activation",
        "playbook",
        ["playbook_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "activation",
        "extra_var_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.alter_column("activation", "is_enabled", server_default=None)
    op.alter_column(
        "activation",
        "execution_environment",
        type_=sa.String(),
        server_default=None,
        nullable=True,
    )
    op.drop_column("activation", "restart_policy")
    op.execute(sa.text('DROP TYPE "restart_policy_enum"'))
    op.execute(sa.text('DROP TYPE "execution_environment_enum"'))
