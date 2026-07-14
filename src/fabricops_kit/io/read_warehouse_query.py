"""Owner file for the ``read_warehouse_query`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import (
    get_spark_session,
    read_warehouse_synapsesql,
    resolve_configured_warehouse_query_target,
    validate_select_query,
)


def read_warehouse_query(
    query: str,
    *,
    target: str = "warehouse",
    spark_session=None,
    context: dict[str, Any] | None = None,
    **options,
):
    """Execute a read-only Warehouse SQL query and return the query result.

    Use this instead of ``read_warehouse_table`` when filtering, projection,
    aggregation, joins, or row limits should be performed before data reaches
    Spark. The supplied SQL is pushed down to the Warehouse SQL serving engine,
    and Spark receives only the query result. Column projection and row
    filtering should be written directly in the SQL. The function accepts a
    ``SELECT`` statement or a CTE beginning with ``WITH`` and ending in a
    ``SELECT``, validates that the query is read-only, and does not
    automatically add filters, projections, or limits beyond what the caller
    includes in the SQL. Reads use the Fabric Warehouse Spark connector rather
    than native Delta access.

    ``read_warehouse_table`` is equivalent to a full-table ``SELECT *`` read.
    ``read_warehouse_query`` provides caller-controlled SQL pushdown. For large
    or repeated PySpark processing, materialize the filtered result into the
    Source Lakehouse as Delta and continue from ``read_lakehouse_table``.

    Rule-of-thumb sizing guidance: small filtered or narrow slices under
    roughly 1 million rows or 1 GB are usually acceptable for ad hoc work;
    1 million to 10 million rows or 1 to 10 GB should be benchmarked first;
    and tables over roughly 10 million rows, over 10 GB, with hundreds of
    columns, or with large text fields should be loaded incrementally into
    Lakehouse Delta before Spark transformations.

    Parameters
    ----------
    query : str
        Read-only SQL ``SELECT`` statement, or a CTE beginning with ``WITH``
        and ending in a ``SELECT``, to execute through the Fabric Warehouse SQL
        serving engine.
    target : str, default="warehouse"
        Logical warehouse target from ``00_env_config``.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.
    **options
        Additional Fabric Warehouse Spark connector reader options. Required
        Fabric connector options are always set from ``00_env_config``.

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame containing exactly the rows and columns returned by
        the supplied Warehouse SQL query.

    Notes
    -----
    FabricOps resolves the configured Warehouse target, sets the Fabric
    connector database to that warehouse artifact, and delegates the read-only
    SQL text to the Fabric Warehouse Spark connector for pushdown. Query callers
    can use two-part names such as ``dbo.orders`` when the configured target
    identifies the warehouse database/artifact. Conceptual example:

    ``df = read_warehouse_query(\"\"\"SELECT DepartmentId, DepartmentName FROM dbo.DimDepartment WHERE IsActive = 1\"\"\")``

    That query returns only the selected columns, filters rows in the
    Warehouse engine, and transfers only the resulting dataset to Spark.

    """
    store = resolve_configured_warehouse_query_target(target, context=context)
    sql = validate_select_query(query)
    return read_warehouse_synapsesql(
        get_spark_session(spark_session),
        store,
        sql,
        options=options,
    )
