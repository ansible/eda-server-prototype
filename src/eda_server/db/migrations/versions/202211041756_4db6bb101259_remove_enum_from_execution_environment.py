"""Remove enum from execution_environment.

Revision ID: 4db6bb101259
Revises: f592f6ef1e3a
Create Date: 2022-11-04 17:56:23.742473+00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4db6bb101259"
down_revision = "f592f6ef1e3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "activation",
        "execution_environment",
        existing_type=postgresql.ENUM(
            "docker",
            "podman",
            "k8s",
            "local",
            name="execution_environment_enum",
        ),
        type_=sa.String(),
        nullable=True,
        server_default=None,
    )
    op.execute(sa.text('DROP TYPE "execution_environment_enum"'))


def downgrade() -> None:
    execution_environment = sa.Enum(
        "docker", "podman", "k8s", "local", name="execution_environment_enum"
    )
    execution_environment.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "activation",
        "execution_environment",
        existing_type=sa.String(),
        type_=execution_environment,
        postgresql_using="execution_environment::execution_environment_enum",
        server_default=sa.text("'docker'::execution_environment_enum"),
        nullable=False,
    )
