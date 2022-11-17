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

"""
Migration utils.

This module contains custom operation directives for alembic.
"""

from typing import Optional

from alembic.operations import MigrateOperation, Operations


@Operations.register_operation("rename_constraint")
class RenameConstraintOp(MigrateOperation):
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


@Operations.register_operation("drop_type")
class DropTypeOp(MigrateOperation):
    """
    Drop type operation.

    Example::

        def downgrade() -> None:
            op.drop_type("type_name")
    """

    def __init__(
        self,
        name: str,
        schema: Optional[str] = None,
    ):
        self.name = name
        self.schema = schema

    @classmethod
    def drop_type(cls, operations, *args, **kwargs):
        return operations.invoke(cls(*args, **kwargs))


@Operations.implementation_for(DropTypeOp)
def drop_type(operations, operation: DropTypeOp):
    name = operation.name
    if operation.schema is not None:
        name = f"{operation.schema}.{name}"
    query = f"DROP TYPE {name}"
    operations.execute(query)
