#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Rename rule set file to rulebook.

Revision ID: 0a069266ef71
Revises: 4c2b57da4a58
Create Date: 2022-08-24 10:53:43.903111+00:00
"""

from alembic import op

import eda_server.db.utils.migrations  # noqa: F401

# revision identifiers, used by Alembic.
revision = "0a069266ef71"
down_revision = "4c2b57da4a58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("rule_set_file", "rulebook")
    op.alter_column(
        "activation",
        column_name="rule_set_file_id",
        new_column_name="rulebook_id",
    )
    op.rename_constraint(
        "activation",
        old_name="fk_activation_rule_set_file_id",
        new_name="fk_activation_rulebook_id",
    )
    op.alter_column(
        "activation_instance",
        column_name="rule_set_file_id",
        new_column_name="rulebook_id",
    )
    op.rename_constraint(
        "activation_instance",
        old_name="fk_activation_instance_rule_set_file_id",
        new_name="fk_activation_instance_rulebook_id",
    )
    op.alter_column(
        "ruleset",
        column_name="rule_set_file_id",
        new_column_name="rulebook_id",
    )
    op.rename_constraint(
        "ruleset",
        old_name="fk_ruleset_rule_set_file_id",
        new_name="fk_ruleset_rulebook_id",
    )


def downgrade() -> None:
    op.rename_constraint(
        "ruleset",
        old_name="fk_ruleset_rulebook_id",
        new_name="fk_ruleset_rule_set_file_id",
    )
    op.alter_column(
        "ruleset",
        column_name="rulebook_id",
        new_column_name="rule_set_file_id",
    )
    op.rename_constraint(
        "activation_instance",
        old_name="fk_activation_instance_rulebook_id",
        new_name="fk_activation_instance_rule_set_file_id",
    )
    op.alter_column(
        "activation_instance",
        column_name="rulebook_id",
        new_column_name="rule_set_file_id",
    )
    op.rename_constraint(
        "activation",
        old_name="fk_activation_rulebook_id",
        new_name="fk_activation_rule_set_file_id",
    )
    op.alter_column(
        "activation",
        column_name="rulebook_id",
        new_column_name="rule_set_file_id",
    )
    op.rename_table("rulebook", "rule_set_file")
