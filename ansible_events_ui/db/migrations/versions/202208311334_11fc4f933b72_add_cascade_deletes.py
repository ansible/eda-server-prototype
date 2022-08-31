"""Add cascade deletes.

Revision ID: 11fc4f933b72
Revises: 57d535d96a60
Create Date: 2022-08-31 13:34:44.968807+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "11fc4f933b72"
down_revision = "57d535d96a60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_activation_rulebook_id", "activation", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_activation_inventory_id", "activation", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_activation_execution_env_id", "activation", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_activation_extra_var_id", "activation", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_activation_playbook_id", "activation", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_activation_execution_env_id"),
        "activation",
        "execution_env",
        ["execution_env_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_activation_rulebook_id"),
        "activation",
        "rulebook",
        ["rulebook_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_activation_extra_var_id"),
        "activation",
        "extra_var",
        ["extra_var_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_activation_inventory_id"),
        "activation",
        "inventory",
        ["inventory_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_activation_playbook_id"),
        "activation",
        "playbook",
        ["playbook_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_activation_instance_rulebook_id",
        "activation_instance",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_activation_instance_extra_var_id",
        "activation_instance",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_activation_instance_inventory_id",
        "activation_instance",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_activation_instance_inventory_id"),
        "activation_instance",
        "inventory",
        ["inventory_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_activation_instance_rulebook_id"),
        "activation_instance",
        "rulebook",
        ["rulebook_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_activation_instance_extra_var_id"),
        "activation_instance",
        "extra_var",
        ["extra_var_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_activation_instance_job_instance_job_instance_id",
        "activation_instance_job_instance",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_activation_instance_job_instance_activation_instance_id",
        "activation_instance_job_instance",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_activation_instance_job_instance_job_instance_id"),
        "activation_instance_job_instance",
        "job_instance",
        ["job_instance_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_activation_instance_job_instance_activation_instance_id"),
        "activation_instance_job_instance",
        "activation_instance",
        ["activation_instance_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_activation_instance_log_activation_instance_id",
        "activation_instance_log",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_activation_instance_log_activation_instance_id"),
        "activation_instance_log",
        "activation_instance",
        ["activation_instance_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_extra_var_project_id", "extra_var", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_extra_var_project_id"),
        "extra_var",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_inventory_project_id", "inventory", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_inventory_project_id"),
        "inventory",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_playbook_project_id", "playbook", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_playbook_project_id"),
        "playbook",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("fk_rule_ruleset_id", "rule", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_rule_ruleset_id"),
        "rule",
        "ruleset",
        ["ruleset_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_rule_set_file_project_id", "rulebook", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_rulebook_project_id"),
        "rulebook",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("fk_ruleset_rulebook_id", "ruleset", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_ruleset_rulebook_id"),
        "ruleset",
        "rulebook",
        ["rulebook_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_ruleset_rulebook_id"), "ruleset", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_ruleset_rulebook_id",
        "ruleset",
        "rulebook",
        ["rulebook_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_rulebook_project_id"), "rulebook", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_rule_set_file_project_id",
        "rulebook",
        "project",
        ["project_id"],
        ["id"],
    )
    op.drop_constraint(op.f("fk_rule_ruleset_id"), "rule", type_="foreignkey")
    op.create_foreign_key(
        "fk_rule_ruleset_id", "rule", "ruleset", ["ruleset_id"], ["id"]
    )
    op.drop_constraint(
        op.f("fk_playbook_project_id"), "playbook", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_playbook_project_id", "playbook", "project", ["project_id"], ["id"]
    )
    op.drop_constraint(
        op.f("fk_inventory_project_id"), "inventory", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_inventory_project_id",
        "inventory",
        "project",
        ["project_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_extra_var_project_id"), "extra_var", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_extra_var_project_id",
        "extra_var",
        "project",
        ["project_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_activation_instance_log_activation_instance_id"),
        "activation_instance_log",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_activation_instance_log_activation_instance_id",
        "activation_instance_log",
        "activation_instance",
        ["activation_instance_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_activation_instance_job_instance_activation_instance_id"),
        "activation_instance_job_instance",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_activation_instance_job_instance_job_instance_id"),
        "activation_instance_job_instance",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_activation_instance_job_instance_activation_instance_id",
        "activation_instance_job_instance",
        "activation_instance",
        ["activation_instance_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_instance_job_instance_job_instance_id",
        "activation_instance_job_instance",
        "job_instance",
        ["job_instance_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_activation_instance_extra_var_id"),
        "activation_instance",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_activation_instance_rulebook_id"),
        "activation_instance",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_activation_instance_inventory_id"),
        "activation_instance",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_activation_instance_inventory_id",
        "activation_instance",
        "inventory",
        ["inventory_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_instance_extra_var_id",
        "activation_instance",
        "extra_var",
        ["extra_var_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_instance_rulebook_id",
        "activation_instance",
        "rulebook",
        ["rulebook_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_activation_playbook_id"), "activation", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_activation_inventory_id"), "activation", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_activation_extra_var_id"), "activation", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_activation_rulebook_id"), "activation", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_activation_execution_env_id"),
        "activation",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_activation_playbook_id",
        "activation",
        "playbook",
        ["playbook_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_extra_var_id",
        "activation",
        "extra_var",
        ["extra_var_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_execution_env_id",
        "activation",
        "execution_env",
        ["execution_env_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_inventory_id",
        "activation",
        "inventory",
        ["inventory_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_activation_rulebook_id",
        "activation",
        "rulebook",
        ["rulebook_id"],
        ["id"],
    )
