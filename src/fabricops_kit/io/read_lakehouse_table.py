"""Owner file for the ``read_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_delta_path, resolve_configured_lakehouse_table


def read_lakehouse_table(
    table_name: str | None = None,
    *,
    table_id: str | None = None,
    target: str = "source",
    schema: str | None = None,
    spark_session=None,
    context: dict[str, Any] | None = None,
    **options,
):
    """Resolve a configured Lakehouse Delta table and return a Spark DataFrame.

    This function represents a complete read of the resolved Delta table.

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
    table_name : str, optional
        Lakehouse table name. Pass schemas with ``schema`` rather than as a
        qualified name. Omit it when ``table_id`` is supplied.
    table_id : str, optional
        Canonical registered table identity. When supplied, FabricOps resolves
        ``table_name``, ``target``, and ``schema`` from the Catalogue.
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

    This function does not read through the Warehouse SQL connector, execute a
    SQL query, write or copy the table, register metadata, create the table,
    mutate the source table, or automatically cache or persist the returned
    DataFrame.

    """
    if table_id is not None:
        if table_name is not None or target != "source" or schema is not None:
            raise ValueError("table_id cannot be combined with table_name, target, or schema.")
        from fabricops_kit.config.shared import resolve_fabric_context
        from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity

        config, env, resolved_context = resolve_fabric_context(context=context)
        identity = resolve_catalogue_table_identity(
            config, env, table_id, spark_session=spark_session, context=resolved_context,
        )
        if identity["store_type"] != "lakehouse":
            raise ValueError(f"table_id {table_id!r} does not identify a Lakehouse table.")
        table_name = identity["table_name"]
        target = identity["target"]
        schema = identity["schema"]
        context = resolved_context
    if table_name is None:
        raise ValueError("Provide table_name or table_id.")
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        target, table_name, schema, context=context
    )
    return read_delta_path(get_spark_session(spark_session), path, options=options)
