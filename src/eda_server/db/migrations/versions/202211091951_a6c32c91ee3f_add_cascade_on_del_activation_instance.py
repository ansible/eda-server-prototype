"""add_cascade_on_del_activation_instance.

Revision ID: a6c32c91ee3f
Revises: 4db6bb101259
Create Date: 2022-11-09 19:51:08.408140+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "a6c32c91ee3f"
down_revision = "4db6bb101259"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_audit_rule_job_instance_id", "audit_rule", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_audit_rule_ruleset_id", "audit_rule", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_audit_rule_rule_id", "audit_rule", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_audit_rule_activation_instance_id",
        "audit_rule",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_audit_rule_job_instance_id"),
        "audit_rule",
        "job_instance",
        ["job_instance_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_audit_rule_activation_instance_id"),
        "audit_rule",
        "activation_instance",
        ["activation_instance_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_audit_rule_ruleset_id"),
        "audit_rule",
        "ruleset",
        ["ruleset_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_audit_rule_rule_id"),
        "audit_rule",
        "rule",
        ["rule_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_audit_rule_rule_id"), "audit_rule", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_audit_rule_ruleset_id"), "audit_rule", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_audit_rule_activation_instance_id"),
        "audit_rule",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_audit_rule_job_instance_id"), "audit_rule", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_audit_rule_activation_instance_id",
        "audit_rule",
        "activation_instance",
        ["activation_instance_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_audit_rule_rule_id", "audit_rule", "rule", ["rule_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_audit_rule_ruleset_id",
        "audit_rule",
        "ruleset",
        ["ruleset_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_audit_rule_job_instance_id",
        "audit_rule",
        "job_instance",
        ["job_instance_id"],
        ["id"],
    )
