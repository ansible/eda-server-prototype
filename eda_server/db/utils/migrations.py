"""
Migration utils.

This module contains custom operation directives for alembic.
"""
from typing import Optional

from alembic.operations import Operations


@Operations.register_operation("rename_constraint")
class RenameConstraintOp:
    """
    Rename constraint operation.

    Example::

        def upgrade() -> None:
            op.rename_constraint(
                "table_name",
                old_name="fk_old",
                new_name="fk_new"
            )

        def downgrade() -> None:
            op.rename_constraint(
                "table_name",
                old_name="fk_new",
                new_name="fk_old",
            )
    """

    def __init__(
        self,
        table_name: str,
        old_name: str,
        new_name: str,
        schema: Optional[str] = None,
    ):
        self.table_name = table_name
        self.old_name = old_name
        self.new_name = new_name
        self.schema = schema

    @classmethod
    def rename_constraint(cls, operations, *args, **kwargs):
        return operations.invoke(cls(*args, **kwargs))


@Operations.implementation_for(RenameConstraintOp)
def rename_constraint(operations, operation: RenameConstraintOp):
    table_name = operation.table_name
    if operation.schema is not None:
        table_name = f"{operation.schema}.{table_name}"
    query = (
        f"ALTER TABLE {table_name} "
        f"RENAME CONSTRAINT {operation.old_name} TO {operation.new_name}"
    )
    operations.execute(query)
