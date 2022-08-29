"""project table add fields

Revision ID: 31e987777ada
Revises: 0a069266ef71
Create Date: 2022-08-24 19:14:09.058949+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "31e987777ada"
down_revision = "0a069266ef71"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("project", sa.Column("name", sa.String(), nullable=True))
    op.add_column(
        "project", sa.Column("description", sa.String(), nullable=True)
    )
    op.add_column(
        "project",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "project",
        sa.Column(
            "modified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("project", "modified_at")
    op.drop_column("project", "created_at")
    op.drop_column("project", "description")
    op.drop_column("project", "name")
