"""Standalone read-only Spark SQL queries against one configured Lakehouse table."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, resolve_configured_lakehouse_table


def read_lakehouse_query(
    query: str,
    *,
    table_name: str,
    store: str = "Bronze",
    schema: str | None = None,
    context: dict[str, Any] | None = None,
):
    """Run read-only Spark SQL against a configured Lakehouse source.

    The query must reference the declared table (or schema.table). CTEs,
    filters, projections, aggregations and self-joins use Spark SQL.
    Simple T-SQL integer TOP projections are translated to LIMIT; unsupported
    T-SQL fails rather than silently changing semantics.

    The source is bound through the configured physical Lakehouse location,
    including cross-workspace stores, not the Spark session's default catalog.
    No pipeline setup, metadata mutation, or contract enforcement is performed.

    Returns a Spark DataFrame. No Spark session is created.

    Parameters
    ----------
    query : str
        One read-only Spark SQL SELECT or CTE referencing the declared source.
        Simple integer T-SQL TOP projections are also supported.
    table_name : str
        Required Lakehouse table name referenced by the query. Supply its schema
        separately with ``schema``.
    store : str, default "Bronze"
        Logical Lakehouse store key configured in ``00_env_config``.
    schema : str | None, optional
        Schema for the declared source in a schema-enabled Lakehouse.
    context : dict[str, Any] | None, optional
        Active Fabric context override containing an existing Spark session
        and configured Lakehouse routing.

    Returns
    -------
    pyspark.sql.DataFrame
        Lazy query result bound to the configured physical source. A downstream
        Spark action evaluates the data.

    Raises
    ------
    ValueError
        If the declared source is invalid, SQL is not read-only, another source
        is referenced, or unsupported T-SQL cannot be converted safely.
    RuntimeError
        If no active Spark session or configured Lakehouse target is available.

    Examples
    --------
    >>> orders_df = read_lakehouse_query(
    ...     "SELECT TOP (5) order_id FROM demo.orders",
    ...     table_name="orders", schema="demo", store="Bronze",
    ... )

    """
    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name is required.")
    spark_session = get_spark_session(context=context)
    _resolved_store, resolved_table, resolved_schema, _path = resolve_configured_lakehouse_table(
        store, table_name, schema, context=context
    )
    # Reuse the orchestrator's deliberately restricted SQL translation and
    # physical-source binding. Import lazily to avoid an IO/pipeline import cycle.
    from fabricops_kit.pipeline.pipeline_read import _lakehouse_query

    identity = {
        "store": store,
        "schema": resolved_schema,
        "table_name": resolved_table,
    }
    dataframe = _lakehouse_query(
        query, identity, context=context, spark_session=spark_session
    )
    if not (context or {}).get("_fabricops_suppress_io_log"):
        print(f"Read from → Object: Lakehouse | Store: {store} | Query: custom SQL")
    return dataframe
