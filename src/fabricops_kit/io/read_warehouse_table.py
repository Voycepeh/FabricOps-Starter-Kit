"""Owner file for the ``read_warehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_warehouse_synapsesql, resolve_configured_warehouse_table


def read_warehouse_table(
    schema: str,
    table_name: str,
    *,
    target: str = "warehouse",
    spark_session=None,
    context: dict[str, Any] | None = None,
    **options,
):
    """Read every row and every column from a Microsoft Fabric Warehouse table.

    This is equivalent to ``SELECT * FROM schema.table_name``. The function
    returns every column and every row exposed by the resolved Warehouse table.
    It does not automatically apply a ``WHERE`` filter, select a subset of
    columns, apply a row limit, aggregate the data, or sample the data. The
    configured Warehouse target is resolved from ``00_env_config``, and the
    read uses the Microsoft Fabric Warehouse Spark connector rather than native
    Delta access.

    Use this callable only for intentional full-table extracts such as small
    lookup tables, reference tables, smoke tests, or cases where every row and
    column is genuinely required. Prefer ``read_warehouse_query`` when
    projection, filtering, aggregation, joins, row limits, or other SQL
    pushdown should occur before data reaches Spark.

    ``read_warehouse_table`` transfers the complete table result to Spark. For
    large or wide Warehouse tables, use ``read_warehouse_query`` so filtering
    and column projection occur in the Warehouse SQL engine before rows are
    transferred to the notebook. As a rule of thumb, small Warehouse reads are
    usually acceptable for reference or ad hoc work, such as narrow tables or
    datasets under roughly 1 million rows or 1 GB. For 1 million to 10 million
    rows, wide tables, or multi-GB data, benchmark first and prefer Lakehouse
    Delta if the data will be reused. For tens of millions of rows, hundreds
    of columns, large text columns, or tables over roughly 10 GB, copy or
    incrementally load the Warehouse data into Lakehouse Delta before Spark
    processing. Avoid a single notebook cell that pulls a very large Warehouse
    table because notebook cells can hit runtime limits.

    Parameters
    ----------
    schema : str
        Physical Warehouse schema name for the source table.
    table_name : str
        Physical Warehouse table name for the source table.
    target : str, default="warehouse"
        Logical Warehouse configuration name from ``00_env_config``. This
        identifies the configured Warehouse target, while ``schema`` and
        ``table_name`` identify the physical Warehouse table.
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
        A Spark DataFrame containing all rows and columns returned from the
        resolved Warehouse table.

    Notes
    -----
    FabricOps resolves the configured Warehouse target and table name, then
    delegates to the Fabric Warehouse Spark connector. Conceptual example:

    ``df = read_warehouse_table(schema="dbo", table_name="DimDepartment")``

    Use ``read_warehouse_query`` instead when you need selected columns, row
    filtering, aggregation, joins, row limits, or other caller-controlled SQL
    pushdown before Spark receives rows.

    """
    store, _schema_value, _table_value, object_name = resolve_configured_warehouse_table(
        target, schema, table_name, context=context
    )
    return read_warehouse_synapsesql(get_spark_session(spark_session), store, object_name, options=options)
