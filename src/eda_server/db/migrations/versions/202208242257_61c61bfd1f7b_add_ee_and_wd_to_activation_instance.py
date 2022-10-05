"""Add execution environment and working directory to activation instance.

Revision ID: 61c61bfd1f7b
Revises: d3abe0785cfd
Create Date: 2022-08-24 22:57:20.017549+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "61c61bfd1f7b"
down_revision = "c1eee0e47fc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "activation_instance",
        sa.Column("execution_environment", sa.String(), nullable=True),
    )
    op.add_column(
        "activation_instance",
        sa.Column("working_directory", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("activation_instance", "execution_environment")
    op.drop_column("activation_instance", "working_directory")
