"""Owner file for the ``read_sql_endpoint_query`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import read_sql_endpoint_query_core


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
    store_name = str(store)
    dataframe = read_sql_endpoint_query_core(
        query,
        store=store,
        spark_session=spark_session,
        context=context,
        options=options,
    )
    if not (context or {}).get("_fabricops_suppress_io_log"):
        print(f"Read from → Object: SQL Endpoint | Store: {store_name} | Query: custom SQL")
    return dataframe
