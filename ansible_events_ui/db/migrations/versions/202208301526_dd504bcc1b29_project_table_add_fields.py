"""project table add fields.

Revision ID: dd504bcc1b29
Revises: 57d535d96a60
Create Date: 2022-08-30 15:26:46.274584+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dd504bcc1b29"
down_revision = "57d535d96a60"
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
