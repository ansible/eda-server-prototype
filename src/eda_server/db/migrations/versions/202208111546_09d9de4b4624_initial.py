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

"""Initial migration.

Revision ID: 09d9de4b4624
Revises:
Create Date: 2022-08-11 13:46:47.214300+00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "09d9de4b4624"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "extra_var",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("extra_var", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_extra_var")),
    )
    op.create_table(
        "inventory",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("inventory", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory")),
    )
    op.create_table(
        "job",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job")),
    )
    op.create_table(
        "job_instance",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_instance")),
    )
    op.create_table(
        "job_instance_event",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("job_uuid", sa.String(), nullable=True),
        sa.Column("counter", sa.Integer(), nullable=True),
        sa.Column("stdout", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_instance_event")),
    )
    op.create_table(
        "playbook",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("playbook", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_playbook")),
    )
    op.create_table(
        "project",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("git_hash", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project")),
    )
    op.create_table(
        "rule_set_file",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("rulesets", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rule_set_file")),
    )
    op.create_table(
        "user",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("id", UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_table(
        "activation",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("rule_set_file_id", sa.Integer(), nullable=True),
        sa.Column("inventory_id", sa.Integer(), nullable=True),
        sa.Column("extra_var_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["extra_var_id"],
            ["extra_var.id"],
            name=op.f("fk_activation_extra_var_id"),
        ),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["inventory.id"],
            name=op.f("fk_activation_inventory_id"),
        ),
        sa.ForeignKeyConstraint(
            ["rule_set_file_id"],
            ["rule_set_file.id"],
            name=op.f("fk_activation_rule_set_file_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activation")),
    )
    op.create_table(
        "activation_instance",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("rule_set_file_id", sa.Integer(), nullable=True),
        sa.Column("inventory_id", sa.Integer(), nullable=True),
        sa.Column("extra_var_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["extra_var_id"],
            ["extra_var.id"],
            name=op.f("fk_activation_instance_extra_var_id"),
        ),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["inventory.id"],
            name=op.f("fk_activation_instance_inventory_id"),
        ),
        sa.ForeignKeyConstraint(
            ["rule_set_file_id"],
            ["rule_set_file.id"],
            name=op.f("fk_activation_instance_rule_set_file_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activation_instance")),
    )
    op.create_table(
        "project_inventory",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("inventory_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["inventory.id"],
            name=op.f("fk_project_inventory_inventory_id"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
            name=op.f("fk_project_inventory_project_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_inventory")),
    )
    op.create_table(
        "project_playbook",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("playbook_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["playbook_id"],
            ["playbook.id"],
            name=op.f("fk_project_playbook_playbook_id"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
            name=op.f("fk_project_playbook_project_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_playbook")),
    )
    op.create_table(
        "project_rule",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("rule_set_file_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
            name=op.f("fk_project_rule_project_id"),
        ),
        sa.ForeignKeyConstraint(
            ["rule_set_file_id"],
            ["rule_set_file.id"],
            name=op.f("fk_project_rule_rule_set_file_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_rule")),
    )
    op.create_table(
        "project_var",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("vars_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
            name=op.f("fk_project_var_project_id"),
        ),
        sa.ForeignKeyConstraint(
            ["vars_id"], ["extra_var.id"], name=op.f("fk_project_var_vars_id")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_var")),
    )
    op.create_table(
        "activation_instance_job_instance",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("activation_instance_id", sa.Integer(), nullable=True),
        sa.Column("job_instance_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_instance_id"],
            ["activation_instance.id"],
            name=op.f(
                "fk_activation_instance_job_instance_activation_instance_id"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["job_instance_id"],
            ["job_instance.id"],
            name=op.f("fk_activation_instance_job_instance_job_instance_id"),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_activation_instance_job_instance")
        ),
    )
    op.create_table(
        "activation_instance_log",
        sa.Column(
            "id", sa.Integer(), sa.Identity(always=True), nullable=False
        ),
        sa.Column("activation_instance_id", sa.Integer(), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("log", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activation_instance_id"],
            ["activation_instance.id"],
            name=op.f("fk_activation_instance_log_activation_instance_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_activation_instance_log")),
    )


def downgrade() -> None:
    op.drop_table("activation_instance_log")
    op.drop_table("activation_instance_job_instance")
    op.drop_table("project_var")
    op.drop_table("project_rule")
    op.drop_table("project_playbook")
    op.drop_table("project_inventory")
    op.drop_table("activation_instance")
    op.drop_table("activation")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    op.drop_table("rule_set_file")
    op.drop_table("project")
    op.drop_table("playbook")
    op.drop_table("job_instance_event")
    op.drop_table("job_instance")
    op.drop_table("job")
    op.drop_table("inventory")
    op.drop_table("extra_var")
