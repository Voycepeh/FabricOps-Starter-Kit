"""Owner file for the ``read_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_delta_path, resolve_configured_lakehouse_table


def read_lakehouse_table(
    table_name: str | None = None,
    *,
    table_id: str | None = None,
    store: str = "Bronze",
    schema: str | None = None,
    context: dict[str, Any] | None = None,
    **options,
):
    """Read a configured Lakehouse Delta table as a lazy Spark DataFrame.

    Spark is resolved automatically from the existing execution session.
    No session is created; Spark-dependent work raises
    ``RuntimeError`` when no session is available.

    Use for managed Delta tables. Apply selection and filtering with normal
    Spark transformations; Delta can push these into the eventual scan.

    Parameters
    ----------
    table_name : str, optional
        Required unless table_id is supplied. Lakehouse table name. Pass schemas with ``schema`` rather than as a
        qualified name. Omit it when ``table_id`` is supplied.
    table_id : str, optional
        Canonical registered table identity. When supplied, FabricOps resolves
        ``table_name``, ``store``, and ``schema`` from the Catalogue. Do not
        combine with table_name, schema, or a non-default store.
    store : str, default="Bronze"
        Logical Lakehouse store key from ``00_env_config``, such as ``bronze`` or
        ``silver``. FabricOps resolves this store key to the configured physical
        Lakehouse and Delta table path.
    schema : str or None, default=None
        Optional schema override for schema-enabled Lakehouses. Supply it
        separately from ``table_name``: use ``schema="sales"`` and
        ``table_name="orders"`` rather than ``table_name="sales.orders"``.
        This is normally omitted for Lakehouses without schemas.
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
    Use either table_name with store and optional schema, or table_id to resolve
    the registered physical location from METADATA_DATA_CATALOGUE. Reader options
    are forwarded to Spark Delta. The call does not register or profile data.

    Examples
    --------
    >>> orders_df = read_lakehouse_table("orders", store="Bronze", schema="demo")
    >>> recent = orders_df.where("order_date >= '2026-01-01'")

    """
    spark_session = get_spark_session(context=context)
    resolved_table_id = table_id
    if table_id is not None:
        if table_name is not None or store != "Bronze" or schema is not None:
            raise ValueError("table_id cannot be combined with table_name, store, or schema.")
        from fabricops_kit.config.shared import resolve_fabric_context
        from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity

        config, active_workspace_id, resolved_context = resolve_fabric_context(context=context)
        identity = resolve_catalogue_table_identity(
            config, active_workspace_id, table_id, spark_session=spark_session, context=resolved_context,
        )
        if str(identity.get("store_type") or identity.get("store_kind") or "").lower() != "lakehouse":
            raise ValueError(f"table_id {table_id!r} does not identify a Lakehouse table.")
        table_name = identity["table_name"]
        store = identity["store"]
        schema = identity["schema"]
        context = resolved_context
    if table_name is None:
        raise ValueError("Provide table_name or table_id.")
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        store, table_name, schema, context=context
    )
    dataframe = read_delta_path(spark_session, path, options=options)
    if resolved_table_id is not None:
        dataframe._fabricops_table_id = str(resolved_table_id)
    if not (context or {}).get("_fabricops_suppress_io_log"):
        parts = ["Object: Lakehouse", f"Store: {store}"]
        if _schema_value:
            parts.append(f"Schema: {_schema_value}")
        parts.append(f"Table: {_table_value}")
        print("Read from → " + " | ".join(parts))
    return dataframe
