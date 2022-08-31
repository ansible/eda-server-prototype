"""project table add fields.

Revision ID: c1eee0e47fc1
Revises: 11fc4f933b72
Create Date: 2022-08-31 18:23:12.353334+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c1eee0e47fc1"
down_revision = "11fc4f933b72"
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
