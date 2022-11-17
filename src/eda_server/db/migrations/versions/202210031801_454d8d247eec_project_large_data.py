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

"""Add large_data_id to project, rename log_id to large_data_id.

Revision ID: 454d8d247eec
Revises: 25bcfbe12475
Create Date: 2022-10-03 18:01:30.836835+00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "454d8d247eec"
down_revision = "25bcfbe12475"
branch_labels = None
depends_on = None


def upgrade() -> None:
    comment = "OID of large object containing project files."
    op.add_column(
        "project",
        sa.Column(
            "large_data_id",
            postgresql.OID(),
            nullable=True,
            comment=comment,
        ),
    )

    op.alter_column(
        "activation_instance",
        "log_id",
        new_column_name="large_data_id",
    )

    # Create trigger function to create large_data_id if that column is null
    op.execute(
        sa.text(
            """
create or replace function trfn_create_lobject()
returns trigger
as $$
begin
    if new.large_data_id is null
    then
        select lo_create(0)
          into new.large_data_id;
    end if;

    return new;
end;
$$ language plpgsql;
            """
        )
    )

    # Create trigger function to cascade delete from project
    # to large object table
    op.execute(
        sa.text(
            """
create or replace function trfn_cascade_delete_lobject()
returns trigger
as $$
begin
    perform lo_unlink(d.large_data_id)
      from deleted_records d;

    return null;
end;
$$ language plpgsql;
            """
        )
    )

    # Create pre-insert row trigger on project table
    op.execute(
        sa.text(
            """
create trigger tr_project_large_data_id
before insert
    on project
   for each row
       execute function trfn_create_lobject();
            """
        )
    )

    # Create post-delete statement trigger on project table
    op.execute(
        sa.text(
            """
create trigger tr_project_cascade_delete_large_data
 after delete
    on project
       referencing old table as deleted_records
   for each statement
       execute function trfn_cascade_delete_lobject();
            """
        )
    )


def downgrade() -> None:
    op.drop_column("project", "large_data_id")

    op.alter_column(
        "activation_instance",
        "large_data_id",
        new_column_name="log_id",
    )

    op.execute(
        sa.text(
            """
drop trigger if exists tr_project_cascade_delete_large_data
  on project;
            """
        )
    )

    op.execute(
        sa.text(
            """
drop trigger if exists tr_project_large_data_id
  on project;
            """
        )
    )

    # Create trigger function to cascade delete from activation_instance
    # to large object table
    op.execute(
        sa.text(
            """
create or replace function trfn_cascade_delete_lobject()
returns trigger
as $$
begin
    perform lo_unlink(d.log_id)
      from deleted_records d;

    return null;
end;
$$ language plpgsql;
            """
        )
    )

    # Create trigger function to create log_id if that column is null
    op.execute(
        sa.text(
            """
create or replace function trfn_create_lobject()
returns trigger
as $$
begin
    if new.log_id is null
    then
        select lo_create(0)
          into new.log_id;
    end if;

    return new;
end;
$$ language plpgsql;
            """
        )
    )
