"""rulebooks add fields.

Revision ID: 53512c168e99
Revises: 25bcfbe12475
Create Date: 2022-10-05 18:22:57.753274+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "53512c168e99"
down_revision = "25bcfbe12475"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "rulebook", sa.Column("description", sa.String(), nullable=True)
    )
    op.add_column(
        "rulebook",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "rulebook",
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("rulebook", "modified_at")
    op.drop_column("rulebook", "created_at")
    op.drop_column("rulebook", "description")
