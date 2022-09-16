"""Add large object logs.

Revision ID: 1285eea03d23
Revises: 0a069266ef71
Create Date: 2022-09-02 17:46:05.902097+00:00

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "1285eea03d23"
down_revision = "34bca36e407d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    comment = (
        "OID of large object containing log(s). "
        "This value will be created by a trigger if not supplied."
    )
    op.add_column(
        "activation_instance",
        sa.Column(
            "log_id",
            postgresql.OID(),
            nullable=True,
            comment=comment,
        ),
    )

    # Create trigger function to create log_id if that column is null
    op.execute(
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

    # Create trigger function to cascade delete from activation_instance
    # to large object table
    op.execute(
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

    # Create pre-insert row trigger on activation_instance table
    op.execute(
        """
create trigger tr_activation_instance_log_id
before insert
    on activation_instance
   for each row
       execute function trfn_create_lobject();
        """
    )

    # Create post-delete statement trigger on activation_instance table
    op.execute(
        """
create trigger tr_activation_instance_cascade_delete_logs
 after delete
    on activation_instance
       referencing old table as deleted_records
   for each statement
       execute function trfn_cascade_delete_lobject();
        """
    )


def downgrade() -> None:
    op.drop_column("activation_instance", "log_id")

    op.execute(
        """
drop trigger if exists tr_activation_instance_cascade_delete_logs
  on activation_instance;
        """
    )

    op.execute(
        """
drop trigger if exists tr_activation_instance_log_id
  on activation_instance;
        """
    )

    op.execute(
        """
drop function if exists trfn_cascade_delete_lobject() ;
        """
    )

    op.execute(
        """
drop function if exists trfn_create_lobject() ;
        """
    )
