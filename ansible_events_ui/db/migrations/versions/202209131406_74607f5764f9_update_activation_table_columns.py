"""Update activation table columns.

Revision ID: 74607f5764f9
Revises: 93a62b2e768b
Create Date: 2022-09-13 14:06:07.046278+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "74607f5764f9"
down_revision = "93a62b2e768b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "activation",
        "activation_status",
        nullable=True,
        new_column_name="status",
    )
    op.alter_column(
        "activation",
        "activation_enabled",
        nullable=False,
        new_column_name="is_enabled",
    )
    op.alter_column(
        "activation",
        "restarted_count",
        nullable=False,
        new_column_name="restart_count",
    )


def downgrade() -> None:
    op.alter_column(
        "activation",
        "status",
        nullable=True,
        new_column_name="activation_status",
    )
    op.alter_column(
        "activation",
        "is_enabled",
        nullable=False,
        new_column_name="activation_enabled",
    )
    op.alter_column(
        "activation",
        "restart_count",
        nullable=False,
        new_column_name="restarted_count",
    )
