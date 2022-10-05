"""Add ruleset created_at, modified_at.

Revision ID: bc14081ad342
Revises: f282d526b775
Create Date: 2022-09-21 20:02:54.926616+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bc14081ad342"
down_revision = "f282d526b775"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ruleset",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "ruleset",
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("ruleset", "modified_at")
    op.drop_column("ruleset", "created_at")
