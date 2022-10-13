"""Create activation_job_instance table.

Revision ID: 5880aea2209e
Revises: abfdc233b4b0
Create Date: 2022-10-13 14:22:05.411526+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5880aea2209e"
down_revision = "abfdc233b4b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activation_job_instance",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("activation_id", sa.Integer(), nullable=True),
        sa.Column("job_instance_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_id"],
            ["activation.id"],
            name=op.f("fk_activation_job_instance_activation_id"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_instance_id"],
            ["job_instance.id"],
            name=op.f("fk_activation_job_instance_job_instance_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activation_job_instance")),
    )


def downgrade() -> None:
    op.drop_table("activation_job_instance")
