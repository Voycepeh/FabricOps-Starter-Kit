"""Owner file for the ``write_warehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import resolve_configured_warehouse_table, validate_dataframe_writer, write_warehouse_synapsesql


def write_warehouse_table(
    df,
    schema: str,
    table_name: str,
    *,
    target: str = "warehouse",
    mode: str = "append",
    repartition: int | None = None,
    options: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
):
    """Write a Spark DataFrame to a Microsoft Fabric warehouse table.

    Use this callable for final serving publication when Warehouse SQL access is
    needed. Keep repeated PySpark transformations in Lakehouse Delta first, then
    publish curated, appropriately sized outputs to Warehouse. Warehouse writes
    use the Fabric connector path rather than native Delta file writes, so
    benchmark wide or multi-GB publications and consider publishing smaller
    serving tables when possible.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to publish.
    schema : str
        Warehouse schema name.
    table_name : str
        Warehouse table name.
    target : str, default="warehouse"
        Logical warehouse target from ``00_env_config``.
    mode : str, default="append"
        Spark writer mode supported by the Fabric connector.
    repartition : int, optional
        Optional positive number of Spark partitions to apply before writing.
        This controls Spark write parallelism and does not create a physically
        partitioned Warehouse table.
    options : dict, optional
        Additional Fabric Warehouse Spark connector writer options. Required
        Fabric connector options are always set from ``00_env_config``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    None
        The DataFrame is written through the Fabric warehouse connector.

    Notes
    -----
    FabricOps resolves the configured Warehouse target and table name, then
    delegates to the Fabric Warehouse Spark connector. ``options`` are passed to
    the underlying ``DataFrameWriter`` after required Fabric connector options.

    """
    validate_dataframe_writer(df)
    if repartition is not None:
        if isinstance(repartition, bool) or not isinstance(repartition, int):
            raise ValueError("repartition must be a positive integer or None")
        if repartition <= 0:
            raise ValueError("repartition must be a positive integer or None")
        df = df.repartition(repartition)

    store, _schema_value, _table_value, object_name = resolve_configured_warehouse_table(
        target, schema, table_name, context=context
    )
    write_warehouse_synapsesql(df, store, object_name, mode=mode, options=options)
