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
    repartition_by=None,
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
    repartition_by : int, str, list, or tuple, optional
        Optional repartitioning applied to the Spark DataFrame before the
        Fabric connector write. This controls Spark write parallelism and does
        not create a physically partitioned Warehouse table. Small serving
        tables normally do not need explicit repartitioning. Repartitioning can
        increase Spark write parallelism by creating additional partitions that
        Spark may process concurrently, subject to available cluster resources
        and destination throughput. Large publications, including workloads
        with millions of rows, may benefit when partition counts are tuned for
        data volume, row width, skew, available Spark resources, connector
        behavior, and Fabric capacity. Millions of rows is an example workload
        size rather than a hard threshold, and row count alone is not
        sufficient for tuning. Too many partitions may reduce performance.
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
    Warehouse ``repartition_by`` affects Spark execution before publication and
    does not physically partition the Warehouse table.

    Examples
    --------
    Small serving tables normally do not need explicit repartitioning.

    ```python
    # Small curated serving table.
    # Keep the DataFrame's existing Spark partitioning.
    write_warehouse_table(
        department_summary_df,
        schema="reporting",
        table_name="department_summary",
        target="warehouse",
        mode="overwrite",
    )
    ```

    For a large serving dataset containing millions of rows, increase Spark
    write parallelism before publishing through the Fabric Warehouse
    connector.

    ```python
    # Large serving dataset containing millions of rows.
    # Increase Spark write parallelism before publishing through the
    # Fabric Warehouse connector.
    write_warehouse_table(
        order_serving_df,
        schema="reporting",
        table_name="orders",
        target="warehouse",
        mode="append",
        repartition_by=32,
    )
    ```

    ``repartition_by=32`` is equivalent to repartitioning the DataFrame before
    the connector write with ``order_serving_df.repartition(32)``.

    ```python
    write_warehouse_table(
        order_serving_df,
        schema="reporting",
        table_name="orders",
        target="warehouse",
        mode="append",
        repartition_by=(32, "order_year", "order_month"),
    )
    ```

    The keyed form distributes rows using the specified columns while
    requesting 32 Spark partitions. It still does not create physical
    Warehouse partitions.

    """
    validate_dataframe_writer(df)
    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            df = (
                df.repartition(*repartition_by)
                if not (repartition_by and isinstance(repartition_by[0], int))
                else df.repartition(repartition_by[0], *repartition_by[1:])
            )
        else:
            df = df.repartition(repartition_by)

    store, _schema_value, _table_value, object_name = resolve_configured_warehouse_table(
        target, schema, table_name, context=context
    )
    write_warehouse_synapsesql(df, store, object_name, mode=mode, options=options)
