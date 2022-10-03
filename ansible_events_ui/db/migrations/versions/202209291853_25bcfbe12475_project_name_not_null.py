"""project_name_not_null.

Revision ID: 25bcfbe12475
Revises: bc14081ad342
Create Date: 2022-09-29 18:53:34.799615+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "25bcfbe12475"
down_revision = "9cdc437024a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "project", "name", existing_type=sa.VARCHAR(), nullable=False
    )

    op.create_check_constraint(
        "ck_project_name_not_empty",
        "project",
        sa.sql.column("name") != "",
    )


def downgrade() -> None:
    op.alter_column(
        "project", "name", existing_type=sa.VARCHAR(), nullable=True
    )

    op.drop_constraint("ck_project_name_not_empty")
