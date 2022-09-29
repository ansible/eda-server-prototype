"""project_name_not_null.

Revision ID: 25bcfbe12475
Revises: bc14081ad342
Create Date: 2022-09-29 18:53:34.799615+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "25bcfbe12475"
down_revision = "bc14081ad342"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "project", "name", existing_type=sa.VARCHAR(), nullable=False
    )

    op.execute(
        sa.text(
            """
alter table project
        add constraint "ck_project_name_not_empty" check (name != '')
;
"""
        )
    )


def downgrade() -> None:
    op.alter_column(
        "project", "name", existing_type=sa.VARCHAR(), nullable=True
    )

    op.execute(
        sa.text(
            """
alter table project
        drop constraint "ck_project_name_not_empty"
;
"""
        )
    )
