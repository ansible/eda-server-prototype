"""
Generalized simple query builders and executors.
"""
from typing import List, Optional, Union

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

# ------------------------------------
#   Generic object executors
# ------------------------------------


async def execute(
    db: AsyncSession, sql: sa.sql.Executable
) -> sa.engine.CursorResult:
    """
    Execute a query and return the created cursor.
    Parameters:
        db:     AsyncSession: Database connection
        sql:    sa.sql.Executable: Query object
    Returns:
        sa.engine.CursorResult: Cursor returned from execution
    """
    cur = await db.execute(sql)
    return cur


async def execute_get_result(
    db: AsyncSession, sql: sa.sql.Executable
) -> sa.engine.Row:
    """
    Execute a query and return the one-record result or None.
    Parameters:
        db:     AsyncSession: Database connection
        sql:    sa.sql.Executable: Query object
    Returns:
        sa.engine.Row: Record from cursor
        None: No record returned
    """
    cur = await execute(db, sql)
    return cur.one_or_none()


async def execute_get_results(
    db: AsyncSession, sql: sa.sql.Executable
) -> sa.engine.CursorResult:
    """Semantic duplicate of 'execute'"""
    return await execute(db, sql)


# ------------------------------------
#   Generic object getters
# ------------------------------------


def build_object_query(
    select_from: Optional[sa.sql.Selectable] = None,
    *,
    select_cols: Optional[
        List[Union[sa.sql.ColumnElement, sa.sql.Selectable]]
    ] = None,
    filters: Optional[sa.sql.ColumnElement] = None,
    group_by: Optional[List[sa.sql.ColumnElement]] = None,
    having: Optional[sa.sql.ColumnElement] = None,
    order_by: Optional[List[sa.sql.ColumnElement]] = None,
) -> sa.sql.Executable:
    """
    Builds a select query and returns an Executable object instance.
    Parameters:
        select_from:    sqlalchemy.sql.Selectable:
                                Table expression from which to select.
        select_cols:    Optional. List of expressions.
                        If omitted, then the value of the select_from
                        parameter is used
        filters:        Optional. sqlalchemy.sql.ColumnElement
                        The filter expressions. For multiple expressions,
                        use sqlalchemy.and_, sqlalchemy.or_ to build
                        the final expression form.
        group_by:       Optional. List of column expressions that will
                        be grouped on.
        having:         Optional. sqlalchemy.sql.ColumnElement
                        Constrain grooping by this expression.
                        Build this using the same methods as filters
        order_by:       Optional. List of column expressions on which to
                        order results.
        Returns:
            sqlalchemy.sql.Executable: The resulting query object.
    """
    if select_cols is None:
        select_cols = [select_from]

    query = sa.select(*select_cols)

    if select_from is not None:
        query = query.select_from(select_from)

    if filters is not None:
        query = query.filter(filters)

    if group_by is not None:
        query = query.group_by(*group_by)

    if having is not None:
        query = query.having(having)

    if order_by is not None:
        query = query.order_by(*order_by)

    return query


async def get_object(
    db: AsyncSession,
    select_from: sa.sql.Selectable,
    *,
    select_cols: Optional[
        List[Union[sa.sql.ColumnElement, sa.sql.Selectable]]
    ] = None,
    filters: Optional[sa.sql.ColumnElement] = None,
    group_by: Optional[List[sa.sql.ColumnElement]] = None,
    having: Optional[sa.sql.ColumnElement] = None,
    order_by: Optional[List[sa.sql.ColumnElement]] = None,
) -> Union[sa.engine.Row, None]:
    """
    Builds and executes a query and returns an expected one-record result
    or None.
    Parameters:
        db:             AsyncSession. The database connection
        select_from:    sqlalchemy.sql.Selectable:
                                Table expression from which to select.
        select_cols:    Optional. List of expressions.
                        If omitted, then the value of the select_from
                        parameter is used
        filters:        Optional. sqlalchemy.sql.ColumnElement
                        The filter expressions. For multiple expressions,
                        use sqlalchemy.and_, sqlalchemy.or_ to build
                        the final expression form.
        group_by:       Optional. List of column expressions that will
                        be grouped on.
        having:         Optional. sqlalchemy.sql.ColumnElement
                        Constrain grooping by this expression.
                        Build this using the same methods as filters
        order_by:       Optional. List of column expressions on which to
                        order results.
        Returns:
            sqlalchemy.engine.Row:  The resulting one record from the query.
            None                    No record returned
    """
    return await execute_get_result(
        db,
        build_object_query(
            select_from,
            select_cols=select_cols,
            filters=filters,
            group_by=group_by,
            having=having,
            order_by=order_by,
        ),
    )


async def get_objects(
    db: AsyncSession,
    select_from: sa.sql.Selectable,
    *,
    select_cols: Optional[
        List[Union[sa.sql.ColumnElement, sa.sql.Selectable]]
    ] = None,
    filters: Optional[sa.sql.ColumnElement] = None,
    group_by: Optional[List[sa.sql.ColumnElement]] = None,
    having: Optional[sa.sql.ColumnElement] = None,
    order_by: Optional[List[sa.sql.ColumnElement]] = None,
) -> sa.engine.CursorResult:
    """
    Builds and executes a query and returns the resulting cursor.
    Parameters:
        db:             AsyncSession. The database connection
        select_from:    sqlalchemy.sql.Selectable:
                                Table expression from which to select.
        select_cols:    Optional. List of expressions.
                        If omitted, then the value of the select_from
                        parameter is used
        filters:        Optional. sqlalchemy.sql.ColumnElement
                        The filter expressions. For multiple expressions,
                        use sqlalchemy.and_, sqlalchemy.or_ to build
                        the final expression form.
        group_by:       Optional. List of column expressions that will
                        be grouped on.
        having:         Optional. sqlalchemy.sql.ColumnElement
                        Constrain grooping by this expression.
                        Build this using the same methods as filters
        order_by:       Optional. List of column expressions on which to
                        order results.
        Returns:
            sqlalchemy.engine.CursorResult:  The resulting cursor
    """
    return await execute_get_results(
        db,
        build_object_query(
            select_from,
            select_cols=select_cols,
            filters=filters,
            group_by=group_by,
            having=having,
            order_by=order_by,
        ),
    )


# ------------------------------------
#   Generic object insert
# ------------------------------------


def build_insert(
    insert_into: sa.sql.TableClause,
    *,
    values: Optional[Union[List[dict], dict]] = None,
    select: Optional[sa.sql.Select] = None,
    returning: Optional[
        List[Union[sa.sql.TableClause, sa.sql.ColumnElement]]
    ] = None,
) -> sa.sql.Insert:
    """
    Builds an insert query and returns the Insert object.
    Data can be specified as a single dict, a list of dict
    or a Select object.
    Parameters:
        insert_into:    sqlalchemy.sql.TableClause:
                                Target table for the new data.
        values:         Optional. List of expressions.
                        If omitted, then the value of the select_from
                        parameter is used
        select:         Optional. sqlalchemy.sql.Select
                        Query that will return data to be put into the
                        target table record(s).
                        Label the column names to match the target
                        table column names
        returning:      Optional. List of column expressions that will
                        be returned from the insert action.
        Returns:
            sqlalchemy.sql.Insert:  The insert query
    """
    ins = sa.insert(insert_into)
    if values is not None:
        ins = ins.values(values)
    elif select is not None:
        if isinstance(select, sa.sql.Select):
            ins_cols = select.selected_columns
        else:
            ins_cols = select.columns
        ins = ins.from_select(ins_cols, select)

    if returning is not None:
        ins = ins.returning(*returning)

    return ins


async def insert_object(
    db: AsyncSession,
    insert_into: sa.sql.TableClause,
    *,
    values: Optional[Union[List[dict], dict]] = None,
    select: Optional[sa.sql.Select] = None,
    returning: Optional[
        List[Union[sa.sql.TableClause, sa.sql.ColumnElement]]
    ] = None,
) -> sa.engine.CursorResult:
    """
    Build and execute an insert query and returns the Insert object.
    Data can be specified as a single dict, a list of dict
    or a Select object.
    Parameters:
        insert_into:    sqlalchemy.sql.TableClause:
                                Target table for the new data.
        values:         Optional. List of expressions.
                        If omitted, then the value of the select_from
                        parameter is used
        select:         Optional. sqlalchemy.sql.Select
                        Query that will return data to be put into the
                        target table record(s).
                        Label the column names to match the target
                        table column names
        returning:      Optional. List of column expressions that will
                        be returned from the insert action.
        Returns:
            sqlalchemy.sql.Insert:  The insert query
    """
    ins = build_insert(
        insert_into, values=values, select=select, returning=returning
    )
    cur = await execute(db, ins)
    return cur
