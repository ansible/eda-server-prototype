"""Convert existing constraints to adhere new naming convention.

Revision ID: a83d0c4f068a
Revises: 42461b4ec88d
Create Date: 2022-08-10 19:08:52.296716

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a83d0c4f068a"
down_revision = "42461b4ec88d"
branch_labels = None
depends_on = None

constraint_name_mapping = {
    "activation": [
        [
            "activation_inventory_id_fkey",
            "fk_activation_inventory_id",
        ],
        [
            "activation_rule_set_file_id_fkey",
            "fk_activation_rule_set_file_id",
        ],
        [
            "activation_extra_var_id_fkey",
            "fk_activation_extra_var_id",
        ],
        [
            "activation_pkey",
            "pk_activation",
        ],
    ],
    "activation_instance": [
        [
            "activation_instance_inventory_id_fkey",
            "fk_activation_instance_inventory_id",
        ],
        [
            "activation_instance_rule_set_file_id_fkey",
            "fk_activation_instance_rule_set_file_id",
        ],
        [
            "activation_instance_extra_var_id_fkey",
            "fk_activation_instance_extra_var_id",
        ],
        [
            "activation_instance_pkey",
            "pk_activation_instance",
        ],
    ],
    "activation_instance_job_instance": [
        [
            "activation_instance_job_instance_pkey",
            "pk_activation_instance_job_instance",
        ],
        [
            "activation_instance_job_instance_activation_instance_id_fkey",
            "fk_activation_instance_job_instance_activation_instance_id",
        ],
        [
            "activation_instance_job_instance_job_instance_id_fkey",
            "fk_activation_instance_job_instance_job_instance_id",
        ],
    ],
    "activation_instance_log": [
        [
            "activation_instance_log_pkey",
            "pk_activation_instance_log",
        ],
        [
            "activation_instance_log_activation_instance_id_fkey",
            "fk_activation_instance_log_activation_instance_id",
        ],
    ],
    "extra_var": [["extra_var_pkey", "pk_extra_var"]],
    "inventory": [
        [
            "inventory_pkey",
            "pk_inventory",
        ]
    ],
    "job": [
        [
            "job_pkey",
            "pk_job",
        ]
    ],
    "job_instance": [["job_instance_pkey", "pk_job_instance"]],
    "job_instance_event": [
        [
            "job_instance_event_pkey",
            "pk_job_instance_event",
        ]
    ],
    "playbook": [["playbook_pkey", "pk_playbook"]],
    "project": [["project_pkey", "pk_project"]],
    "project_inventory": [
        [
            "project_inventory_pkey",
            "pk_project_inventory",
        ],
        [
            "project_inventory_inventory_id_fkey",
            "fk_project_inventory_inventory_id",
        ],
        [
            "project_inventory_project_id_fkey",
            "fk_project_inventory_project_id",
        ],
    ],
    "project_playbook": [
        [
            "project_playbook_project_id_fkey",
            "fk_project_playbook_project_id",
        ],
        [
            "project_playbook_pkey",
            "pk_project_playbook",
        ],
        [
            "project_playbook_playbook_id_fkey",
            "fk_project_playbook_playbook_id",
        ],
    ],
    "project_rule": [
        [
            "project_rule_pkey",
            "pk_project_rule",
        ],
        [
            "project_rule_project_id_fkey",
            "fk_project_rule_project_id",
        ],
        [
            "project_rule_rule_set_file_id_fkey",
            "fk_project_rule_rule_set_file_id",
        ],
    ],
    "project_var": [
        [
            "project_var_project_id_fkey",
            "fk_project_var_project_id",
        ],
        [
            "project_var_pkey",
            "pk_project_var",
        ],
        [
            "project_var_vars_id_fkey",
            "fk_project_var_vars_id",
        ],
    ],
    "rule_set_file": [["rule_set_file_pkey", "pk_rule_set_file"]],
    "user": [["user_pkey", "pk_user"]],
}


def upgrade() -> None:
    for table, names in constraint_name_mapping.items():
        for old_name, new_name in names:
            rename_constraint(table, old_name, new_name)


def downgrade() -> None:
    for table, names in constraint_name_mapping.items():
        for new_name, old_name in names:
            rename_constraint(table, old_name, new_name)


def rename_constraint(table, old_name, new_name) -> None:
    query = 'ALTER TABLE "{0}" RENAME CONSTRAINT "{1}" TO "{2}"'.format(
        table, old_name, new_name
    )
    op.execute(sa.text(query))
