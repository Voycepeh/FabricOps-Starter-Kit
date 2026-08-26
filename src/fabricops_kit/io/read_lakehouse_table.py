"""Owner file for the ``read_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import (
    apply_lakehouse_processing_scope,
    get_spark_session,
    read_delta_path,
    resolve_configured_lakehouse_table,
    validate_processing_scope,
)


def read_lakehouse_table(
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
    spark_session=None,
    context: dict[str, Any] | None = None,
    processing_scope: dict[str, Any] | None = None,
    **options,
):
    """Resolve a configured Lakehouse Delta table and return a Spark DataFrame.

    By default, this function represents a complete read of the resolved Delta
    table. When ``processing_scope`` is supplied, FabricOps applies its
    governed watermark or logical-partition filter directly to the lazy Delta
    read plan.

    The returned Spark DataFrame is lazy. Calling ``read_lakehouse_table``
    constructs the DataFrame plan, and Spark reads data only when a downstream
    action executes, such as ``display``, ``count``, ``collect``, or a
    DataFrame write. Subsequent Spark transformations may still allow Delta
    column pruning and predicate pushdown during execution.

    Lakehouse Delta is the preferred source for repeated PySpark
    transformations in FabricOps. Use this callable for managed Lakehouse
    tables, data already stored in OneLake Delta format, and source or
    unified data processing inside Fabric notebooks. When source data starts in
    a Fabric Warehouse, save large or repeatedly used data into the
    Source Lakehouse as Delta first, then read it with this callable.

    Parameters
    ----------
    table_name : str
        Lakehouse table name. Pass schemas with ``schema`` rather than as a
        qualified name.
    target : str, default="source"
        Logical Lakehouse target from ``00_env_config``, such as ``source`` or
        ``unified``. FabricOps resolves this target to the configured physical
        Lakehouse and Delta table path.
    schema : str or None, default=None
        Optional schema override for schema-enabled Lakehouses. Supply it
        separately from ``table_name``: use ``schema="sales"`` and
        ``table_name="orders"`` rather than ``table_name="sales.orders"``.
        This is normally omitted for Lakehouses without schemas.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.
    processing_scope : dict[str, Any], optional
        Runtime scope returned in ``read_pipeline_prep(...)["scope"]``. A
        watermark scope reads ``(lower_bound, upper_bound]`` and a partition
        scope reads only its listed logical partition values. ``skip`` raises
        before the Delta table is resolved or read. Omit this argument to keep
        the existing complete-table behavior.
    **options
        Additional Spark Delta ``DataFrameReader`` options forwarded to the
        Delta reader. These options do not provide FabricOps-level filtering or
        projection.

    Returns
    -------
    pyspark.sql.DataFrame
        A lazy Spark DataFrame representing the governed rows and all columns
        in the resolved Lakehouse Delta table. The data is evaluated when a
        downstream Spark action runs.

    Raises
    ------
    ValueError
        If ``processing_scope`` is malformed or resolves the source to
        ``skip``.

    Notes
    -----
    FabricOps resolves the configured Lakehouse Tables path from
    ``00_env_config`` and then delegates to Spark's Delta reader with any
    supplied reader options. Filtering and column selection are applied later
    through normal Spark DataFrame operations. Conceptual examples:

    ``df = read_lakehouse_table(table_name="orders", target="source")``

    ``df = read_lakehouse_table(table_name="orders", target="source", schema="sales")``

    ``orders_df = read_lakehouse_table(table_name="sales_orders", target="source")``

    ``recent_orders_df = orders_df.select("order_id", "customer_id", "order_date", "amount").where("order_date >= '2026-01-01'")``

    ``source_df = read_lakehouse_table(table_name="orders", processing_scope=read_prep["scope"])``

    Governed watermark scopes use ``column > lower_bound`` and
    ``column <= upper_bound``. Spark may push these filters and compatible
    downstream projections into the Delta scan during execution.

    This function does not read through the Warehouse SQL connector, execute a
    SQL query, write or copy the table, register metadata, create the table,
    mutate the source table, or automatically cache or persist the returned
    DataFrame.

    """
    scope = None if processing_scope is None else validate_processing_scope(processing_scope)
    if scope is not None and scope["type"] == "skip":
        raise ValueError("The current source was resolved to skip and must not be read.")
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        target, table_name, schema, context=context
    )
    dataframe = read_delta_path(get_spark_session(spark_session), path, options=options)
    return dataframe if scope is None else apply_lakehouse_processing_scope(dataframe, scope)
