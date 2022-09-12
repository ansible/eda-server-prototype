"""Add audit rules table.

Revision ID: a65f108090b6
Revises: 61c61bfd1f7b
Create Date: 2022-09-12 18:02:43.598662+00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a65f108090b6"
down_revision = "61c61bfd1f7b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_rule",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column(
            "fired_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "definition",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column("ruleset_id", sa.Integer(), nullable=False),
        sa.Column("activation_instance_id", sa.Integer(), nullable=False),
        sa.Column("job_instance_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_instance_id"],
            ["activation_instance.id"],
            name=op.f("fk_audit_rule_activation_instance_id"),
        ),
        sa.ForeignKeyConstraint(
            ["job_instance_id"],
            ["job_instance.id"],
            name=op.f("fk_audit_rule_job_instance_id"),
        ),
        sa.ForeignKeyConstraint(
            ["rule_id"], ["rule.id"], name=op.f("fk_audit_rule_rule_id")
        ),
        sa.ForeignKeyConstraint(
            ["ruleset_id"],
            ["ruleset.id"],
            name=op.f("fk_audit_rule_ruleset_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_rule")),
    )


def downgrade() -> None:
    op.drop_table("audit_rule")
