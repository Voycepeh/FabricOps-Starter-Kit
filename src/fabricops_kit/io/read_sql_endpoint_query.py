"""Owner file for the ``read_sql_endpoint_query`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import (
    get_spark_session,
    read_warehouse_synapsesql,
    resolve_configured_sql_endpoint_store,
    validate_select_query,
)


def read_sql_endpoint_query(
    query: str,
    *,
    store: str,
    spark_session=None,
    context: dict[str, Any] | None = None,
    **options,
):
    """Execute a read-only SQL query against a configured Fabric SQL endpoint.

    Use this when the configured target may be either a Warehouse or a
    Lakehouse SQL analytics endpoint. The query must be a read-only ``SELECT``
    statement, or a CTE beginning with ``WITH`` and ending in a ``SELECT``.

    Parameters
    ----------
    query : str
        Read-only SQL statement to execute through the configured Fabric SQL
        endpoint.
    store : str
        Logical Warehouse or Lakehouse store key from ``00_env_config``.
    spark_session : object, optional
        Spark session to use instead of the active notebook session.
    context : dict[str, Any], optional
        Active Fabric context override.
    **options
        Additional Fabric connector reader options.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame containing the rows and columns returned by the query.

    Raises
    ------
    ValueError
        If the query is not read-only or the configured store is neither a
        Warehouse nor a Lakehouse.

    Notes
    -----
    This is the general SQL-endpoint reader for configured Fabric data items.
    Use ``read_warehouse_query`` when the caller specifically requires a
    Warehouse-only contract.

    Examples
    --------
    >>> df = read_sql_endpoint_query(
    ...     "SELECT TOP (10) * FROM dbo.orders",
    ...     store="Gold",
    ...     spark_session=spark,
    ... )

    """
    configured_store, _env = resolve_configured_sql_endpoint_store(store, context=context)
    sql = validate_select_query(query)
    dataframe = read_warehouse_synapsesql(
        get_spark_session(spark_session),
        configured_store,
        sql,
        database_name=store,
        options=options,
    )
    if not (context or {}).get("_fabricops_suppress_io_log"):
        object_name = "Warehouse" if configured_store.kind == "warehouse" else "Lakehouse"
        print(f"Read from → Object: {object_name} | Store: {store} | Query: custom SQL")
    return dataframe
