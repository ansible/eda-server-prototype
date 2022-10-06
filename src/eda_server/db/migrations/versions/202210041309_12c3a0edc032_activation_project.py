"""Adds project to activation.

Revision ID: 12c3a0edc032
Revises: 454d8d247eec
Create Date: 2022-10-04 13:09:50.026149+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "12c3a0edc032"
down_revision = "454d8d247eec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "activation_instance",
        sa.Column("project_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_activation_instance_project_id"),
        "activation_instance",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_activation_instance_project_id"),
        "activation_instance",
        type_="foreignkey",
    )
    op.drop_column("activation_instance", "project_id")
