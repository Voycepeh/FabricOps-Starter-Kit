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
    """Resolve a configured Warehouse table and publish the DataFrame through the connector.

    The function performs an immediate connector write using the selected mode
    and optional Spark repartitioning. Use this callable for final serving
    publication when Warehouse SQL access is needed. Keep repeated PySpark
    transformations in Lakehouse Delta first, then publish curated,
    appropriately sized outputs to Warehouse. Warehouse writes use the Fabric
    connector path rather than native Delta file writes, so benchmark wide or
    multi-GB publications and consider publishing smaller serving tables when
    possible.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to publish.
    schema : str
        Warehouse schema name.
    table_name : str
        Warehouse table name.
    target : str, default="warehouse"
        Logical Warehouse target from ``00_env_config``. FabricOps resolves
        the logical target, workspace ID, Warehouse item ID, Warehouse
        database name, schema, and table name. The connector destination is
        conceptually ``<warehouse_name>.<schema>.<table_name>`` and is not a
        native Delta path write.
    mode : str, default="append"
        Value passed directly to Spark's ``DataFrameWriter`` and then applied
        through the Fabric Warehouse connector. Supported destination behavior
        can depend on the connector, destination table state, and active
        Fabric runtime.

        ``append`` adds rows to the destination. Rerunning the same
        publication may duplicate rows.

        ``overwrite`` requests replacement behavior through the connector and
        should be treated as destructive.

        This function does not execute SQL ``MERGE``, perform an upsert, match
        business keys, deduplicate records, or provide idempotent publication.
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
        sufficient for tuning. Too many partitions may reduce performance or
        increase connector overhead.

        ``repartition_by=32`` is equivalent to ``df.repartition(32)``.
        ``repartition_by="department"`` is equivalent to
        ``df.repartition("department")``.
        ``repartition_by=["year", "month"]`` is equivalent to
        ``df.repartition("year", "month")``.
        ``repartition_by=(32, "year", "month")`` is equivalent to
        ``df.repartition(32, "year", "month")``.

        Repartitioning affects Spark execution and connector parallelism. It
        does not create physical Warehouse table partitions.
    options : dict, optional
        Additional Fabric Warehouse Spark connector writer options. FabricOps
        sets the resolved Workspace ID and Warehouse item ID before applying
        caller options, then forwards caller options to the connector writer.
        Do not pass custom options that replace the resolved Workspace ID,
        Warehouse item ID, or other destination identity settings.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    None
        The function performs the Fabric Warehouse connector write before
        returning.

    Notes
    -----
    FabricOps resolves the configured Warehouse target and table name, then
    delegates to the Fabric Warehouse Spark connector. ``options`` are passed to
    the underlying ``DataFrameWriter`` after required Fabric connector options.
    Warehouse ``repartition_by`` affects Spark execution before publication and
    does not physically partition the Warehouse table.

    The function requires Microsoft Fabric Spark and the
    ``com.microsoft.spark.fabric`` Warehouse connector. It is not expected to
    work in a generic local Spark environment without that connector.

    The connector write is executed before the function returns. The function
    does not return a lazy publication plan. It returns ``None`` after
    successful publication or raises an underlying Spark or connector error.

    Table creation, replacement, and schema handling are delegated to the
    Fabric Warehouse connector. The function does not independently issue
    Warehouse DDL, pre-create schemas or tables, or verify whether the caller
    has permissions to create or overwrite the destination.

    The function does not prevalidate Warehouse column names,
    SQL-compatible data types, destination column order, nullability, string
    lengths, decimal precision or scale, existing destination schema, or
    primary keys or constraints. Any incompatibility is handled by Spark and
    the Fabric connector.

    This function does not automatically register catalogue metadata,
    register lineage, execute guardrails, validate a contract, validate
    publication approval, apply access governance, create a semantic model, or
    refresh Power BI content.

    Comparison:

    | Function | Destination | Write mechanism | Physical partitioning |
    | --- | --- | --- | --- |
    | ``write_lakehouse_table`` | Lakehouse ``Tables`` Delta path | Native Spark Delta writer | Supported through ``partition_by`` |
    | ``write_warehouse_table`` | Fabric Warehouse table | Fabric Warehouse Spark connector | Not created by this function |

    Both functions default to append behavior, both can duplicate rows when
    the same data is published repeatedly, neither performs merge or upsert
    logic, and repartitioning affects Spark execution in both functions.

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
    requesting 32 Spark partitions. It still does not create physical Warehouse partitions.

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
