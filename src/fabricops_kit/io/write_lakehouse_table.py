"""Owner file for the ``write_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import (
    normalize_write_mode,
    resolve_configured_lakehouse_table,
    validate_dataframe_writer,
    write_delta_path,
)


def write_lakehouse_table(
    df,
    table_name: str,
    *,
    target: str = "unified",
    schema=None,
    mode="append",
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose=True,
    context=None,
):
    """Resolve a configured Lakehouse table and write the DataFrame to its Delta path.

    The function performs an immediate Spark write using the selected write
    mode and optional execution and storage partitioning settings. Lakehouse
    Delta is optimized for FabricOps PySpark processing and reuse. Prefer this
    callable for repeated PySpark processing and reusable intermediate,
    Unified, Product, and metadata Delta outputs that will be read repeatedly
    by Spark. Publish selected serving outputs to Warehouse separately when
    SQL serving is required.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    table_name : str
        Lakehouse table name. Supply ``schema`` and ``table_name`` separately;
        do not pass a qualified name such as ``schema.table`` through
        ``table_name``.
    target : str, default="unified"
        Logical Lakehouse target from ``00_env_config``. FabricOps resolves
        the selected environment, workspace, Lakehouse item, optional schema,
        table name, and OneLake Delta path under the Lakehouse ``Tables``
        area.
    schema : str or None, default=None
        Optional schema override for schema-enabled Lakehouses.
    mode : str, default="append"
        Spark Delta write mode.

        ``append`` adds rows to the existing destination or creates it when
        absent. Rerunning the same input can create duplicate rows. No
        business-key matching, deduplication, or idempotency check is
        performed.

        ``overwrite`` replaces the destination data according to Spark Delta
        writer behavior and should be treated as destructive.

        ``errorifexists`` fails when the destination already exists.

        ``ignore`` skips the write when the destination already exists.

        This function does not perform a Delta ``MERGE``, upsert,
        update-on-match, delete-on-missing, or key-based deduplication.
    partition_by : str or list[str], optional
        Column or columns used to create physical Delta table partitions in
        storage. Use this for stable, commonly filtered, relatively
        low-cardinality columns such as year or month when that layout improves
        downstream reads. ``partition_by`` affects the physical Delta table
        layout rather than Spark execution parallelism. High-cardinality
        partition columns can create excessive folders and small files, and
        the function does not inspect or reconcile an existing table's
        partition layout before writing.
    repartition_by : int, str, list, or tuple, optional
        Optional repartitioning applied to the Spark DataFrame before the
        write. This changes the Spark partition distribution and can increase
        Spark write parallelism by creating additional partitions that Spark
        may process concurrently, subject to available cluster resources and
        destination throughput. Small DataFrames normally do not need explicit
        repartitioning. Large datasets, including workloads with millions of
        rows, may benefit when partition counts are tuned for data volume, row
        width, skew, file sizes, and available Fabric Spark capacity. Millions
        of rows is an example workload size rather than a hard threshold. Row
        count alone is not sufficient for tuning.
        Excessive repartitioning can add shuffle cost, scheduler overhead, and
        many small files.

        ``repartition_by=32`` is equivalent to ``df.repartition(32)``.
        ``repartition_by="department"`` is equivalent to
        ``df.repartition("department")``.
        ``repartition_by=["year", "month"]`` is equivalent to
        ``df.repartition("year", "month")``.
        ``repartition_by=(32, "year", "month")`` is equivalent to
        ``df.repartition(32, "year", "month")``.

        Repartitioning changes the DataFrame used for the write but does not
        mutate the caller's original DataFrame binding.
    options : dict, optional
        Additional Spark Delta ``DataFrameWriter`` options forwarded before
        saving the configured Lakehouse ``Tables`` path, such as
        ``mergeSchema``, ``overwriteSchema``, and other standard Delta writer
        options supported by the active Spark runtime. FabricOps forwards
        these options and does not validate their compatibility.
    verbose : bool, default=True
        Whether to print the resolved output path before writing.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    None
        The function performs the Spark Delta write before returning.

    Notes
    -----
    FabricOps resolves the configured Lakehouse Tables path from
    ``00_env_config`` and then delegates to Spark's Delta writer with any
    supplied writer options. ``repartition_by`` affects Spark execution before
    the write, while ``partition_by`` affects the physical Delta table layout
    on storage. The function triggers a Spark write job, does not return a
    lazy write plan, and returns ``None`` only after the write completes or
    Spark raises an error. It may create the Delta destination when it does
    not already exist, subject to Spark write behavior and the selected mode.

    The function does not automatically validate the DataFrame against a data
    contract, match business keys, add missing columns, reorder columns, cast
    incompatible types, reconcile schema differences, enable schema evolution,
    validate nullability, or check existing partition columns. Schema
    evolution or overwrite-schema behavior depends on supplied Spark Delta
    writer options where supported.

    This function only writes the DataFrame. It does not automatically
    register catalogue metadata, register lineage, profile the table, execute
    guardrails, validate a data contract, apply access governance, or create
    stewardship or agreement records.

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
    Small DataFrames normally do not need explicit repartitioning.

    ```python
    # Small lookup or reference table.
    # Keep the DataFrame's existing Spark partitioning.
    write_lakehouse_table(
        country_lookup_df,
        table_name="country_lookup",
        target="unified",
        schema=UNIFIED_SCHEMA,
        mode="overwrite",
    )
    ```

    For a large fact dataset containing millions of rows, you can increase
    Spark write parallelism before the write while also physically
    partitioning the Delta table by commonly filtered date columns.

    ```python
    # Large fact dataset containing millions of rows.
    # Repartition into more Spark tasks before writing, while physically
    # partitioning the Delta table by commonly filtered date columns.
    write_lakehouse_table(
        orders_df,
        table_name="orders",
        target="unified",
        schema=UNIFIED_SCHEMA,
        mode="append",
        repartition_by=(32, "order_year", "order_month"),
        partition_by=["order_year", "order_month"],
    )
    ```

    ``repartition_by=(32, "order_year", "order_month")`` is equivalent to
    ``orders_df.repartition(32, "order_year", "order_month")``. Spark can
    process and write those partitions concurrently, subject to the available
    executors and Fabric capacity. ``partition_by=["order_year",
    "order_month"]`` creates the physical Delta directory partitioning. The
    value ``32`` is illustrative and should be benchmarked rather than treated
    as a universal recommendation.

    When physical Delta partitioning is not required, you can increase Spark
    write parallelism without changing the destination table layout.

    ```python
    write_lakehouse_table(
        events_df,
        table_name="events",
        target="unified",
        schema=UNIFIED_SCHEMA,
        mode="append",
        repartition_by=32,
    )
    ```

    This increases the number of Spark partitions before the write without
    physically partitioning the destination Delta table.

    """
    validate_dataframe_writer(df)
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        target, table_name, schema, context=context
    )
    normalized_mode = normalize_write_mode(mode)
    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            df = (
                df.repartition(*repartition_by)
                if not (repartition_by and isinstance(repartition_by[0], int))
                else df.repartition(repartition_by[0], *repartition_by[1:])
            )
        else:
            df = df.repartition(repartition_by)
    if verbose:
        print(f"Writing Lakehouse table to {path}")
    write_delta_path(df, path, mode=normalized_mode, partition_by=partition_by, options=options)
