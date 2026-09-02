"""Owner file for the ``write_warehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import (
    execute_warehouse_processing,
    repartition_dataframe_for_write,
    resolve_configured_warehouse_table,
    validate_dataframe_writer,
    write_warehouse_synapsesql,
)


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
    load_strategy: str | None = None,
    load_strategy_parameters: dict[str, Any] | None = None,
    completion_context: dict[str, Any] | None = None,
):
    """Write a Spark DataFrame to a configured Fabric Warehouse table.

    ``write_warehouse_table`` writes a Spark DataFrame to a Fabric Warehouse
    table through the configured Warehouse write path. It supports Spark-side
    repartitioning before data is transferred so large datasets can use
    multiple Spark tasks concurrently during the write preparation and
    connector transfer stages.

    Warehouse repartitioning controls Spark execution only. It does not create
    physical Warehouse table partitions and is not equivalent to lakehouse
    ``partition_by``.

    Use this when a prepared and validated Spark DataFrame must be stored in a
    Fabric Warehouse. For small datasets, the default write path is normally
    sufficient. For large datasets containing millions of rows, use
    ``repartition_by`` when the DataFrame has too few partitions or when more
    balanced Spark-side write concurrency is required. Use
    ``write_lakehouse_table`` when the target is a Delta table in a lakehouse
    or when physical Delta partitioning is required.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to transfer into the Warehouse. The original DataFrame
        object is not modified; a repartitioned DataFrame is used for the
        write when requested.
    schema : str
        Warehouse schema containing the target table, such as ``dbo``. This is
        part of the Warehouse object identity and is unrelated to Spark schema
        inference.
    table_name : str
        Warehouse table name.
    target : str, default="warehouse"
        Logical Warehouse target from ``00_env_config``. FabricOps resolves
        the logical target, workspace ID, Warehouse item ID, Warehouse database
        name, schema, and table name.
    mode : {"append", "overwrite", "errorifexists", "ignore"}, default="append"
        Requested Warehouse write behaviour passed to the Fabric Warehouse
        Spark connector. ``append`` adds rows and can duplicate repeated
        publications. ``overwrite`` requests replacement behaviour and should
        be treated as destructive. Other supported modes are passed through to
        Spark/connector semantics.
    repartition_by : int or str or list[str] or tuple[str, ...], optional
        Optional Spark-side repartitioning applied before the Warehouse
        connector is invoked. A positive integer controls the number of Spark
        execution partitions. A column name or collection of column names
        redistributes records by those keys. A list or tuple beginning with a
        positive integer supplies both the partition count and the distribution
        columns. This controls Spark processing for the current write and does
        not configure the Warehouse table's physical design.
    options : dict, optional
        Additional Fabric Warehouse Spark connector writer options. FabricOps
        sets the resolved Workspace ID and Warehouse item ID before applying
        caller options, then forwards caller options to the connector writer.
        Do not pass custom options that replace the resolved destination
        identity settings.
    context : dict[str, Any], optional
        Active Fabric context override.
    load_strategy : {"overwrite", "append", "scd1", "scd2"}, optional
        Governed strategy returned by :func:`write_pipeline_prep`.
    load_strategy_parameters : dict, optional
        Governed strategy parameters. ``scd1`` requires ``key_columns``;
        ``scd2`` also requires ``effective_column`` and may supply
        ``tracked_columns``.
    completion_context : dict, optional
        Governed source-completion context returned by
        :func:`write_pipeline_prep`. Target Lineage and any partition completion
        state are persisted after the write. Watermark progress is already
        stored on successfully published target rows.

    Returns
    -------
    None
        The function performs the Fabric Warehouse connector write before
        returning.

    Notes
    -----
    Governed completion
        The Warehouse mutation completes before Lineage or partition completion
        is persisted. Watermark correctness has no post-write checkpoint:
        ``_watermark_value`` advances with target publication. SCD1 and SCD2
        replay is deterministic; governed incremental-watermark append is
        rejected without deterministic identity. Independent concurrent jobs
        remain subject to Warehouse transaction and locking semantics.

    Parallel processing and write concurrency
        Spark processes DataFrame partitions concurrently. Before invoking the
        Warehouse connector, ``write_warehouse_table`` can repartition the
        input DataFrame so the transfer is prepared and executed through a
        larger or more appropriately distributed set of Spark tasks.

        This is Spark distributed processing. The function does not create
        Python threads, does not run several independent Warehouse write calls,
        and does not provide unrestricted concurrent mutation of the same
        Warehouse table.

        The repartitioned DataFrame is the DataFrame passed to the Warehouse
        connector.

    Integer repartitioning
        Passing a positive integer creates that number of Spark DataFrame
        partitions before the Warehouse write path is invoked by calling
        ``df.repartition(number)``. For a large fact dataset, this allows Spark
        to prepare and transfer multiple partitions concurrently, subject to
        available executor capacity and Warehouse connector behaviour or
        limits.

    Column-based repartitioning
        Passing a column name, string-only list, or string-only tuple repartitions
        the Spark DataFrame by the selected keys before the Warehouse connector
        receives it by calling ``df.repartition(*columns)``. A list or tuple
        such as ``(32, "academic_year", "semester")`` calls
        ``df.repartition(32, "academic_year", "semester")`` and controls both
        Spark task count and distribution keys for the current write. This
        affects only Spark-side row distribution for the current write. It does
        not declare Warehouse
        partitions, indexes, distribution keys, clustered columns, or any other
        physical Warehouse design.

    No ``partition_by`` for Warehouse
        ``write_warehouse_table`` must not expose or document lakehouse-style
        ``partition_by`` behaviour. Physical Delta partitioning belongs only to
        ``write_lakehouse_table``. Warehouse physical design is managed through
        Warehouse-supported table and indexing features, not through Spark
        DataFrame ``partitionBy``.

    Implementation sequence
        The function validates the DataFrame writer, validates
        ``repartition_by``, calls ``df.repartition(number)`` for a positive
        integer, ``df.repartition(*columns)`` for a column name/list/tuple, or
        ``df.repartition(number, *columns)`` when a list or tuple begins with a
        positive integer, resolves the Warehouse connection and table
        identity, passes the repartitioned DataFrame into the Warehouse write
        connector, executes the requested connector write mode, and returns
        ``None``. Governed SCD strategies use a unique run-scoped Warehouse
        staging table and transactional T-SQL target mutation; append and
        overwrite continue to use the direct ``synapsesql`` write path. The
        transaction drops its staging table, and failures also trigger a
        best-effort Python-side cleanup attempt without masking the original
        publication error.

    Performance notes
        Repartitioning can improve write throughput when the existing
        DataFrame has too few partitions for the available Spark executors. It
        also requires a Spark shuffle. Excessive partitions may increase
        scheduling overhead, transfer overhead, or connector pressure.
        Column-based repartitioning should avoid severely skewed or very
        low-cardinality keys when they would create uneven task sizes.
        Warehouse write concurrency is also constrained by the connector,
        Warehouse capacity, transaction behaviour, table locks, and
        service-level limits. ``repartition_by`` increases Spark-side
        parallelism but does not guarantee linear write-speed improvement.

    Concurrency safety clarification
        Parallel Spark tasks within one ``write_warehouse_table`` call are not
        the same as several notebooks or jobs writing to the same Warehouse
        table concurrently. The function does not coordinate multiple
        independent writers, serialize competing jobs, retry transaction
        conflicts, or guarantee safe simultaneous overwrite operations.

    Errors and edge cases
        ``repartition_by`` rejects zero or negative integers, missing columns
        when DataFrame columns are available, unsupported value types, empty lists or
        tuples, and non-string column values after any leading partition count.
        Schema or table not found, unsupported write modes, authentication
        failure, connector failure, Warehouse permission failure, unsupported
        Spark-to-Warehouse type conversion, connector-managed transfer or
        staging failure, transaction or lock conflicts,
        empty DataFrames, large transfer timeout or resource exhaustion, and
        accidental use of the original DataFrame after repartitioning are
        handled by Spark, the Fabric connector, or Warehouse runtime errors.

    Warehouse SCD processing
        ``scd1`` performs a key-based upsert without deleting missing target
        rows. ``scd2`` compares non-key business columns, closes changed current
        rows, and inserts one new current version in the same transaction.
        Duplicate incoming keys, backwards effective times, incompatible
        schemas, and multiple target current rows fail before target commit.
        Replaying unchanged input does not add rows. Independent jobs can still
        encounter Warehouse transaction or locking conflicts.

    Side effects
        This function performs a physical Warehouse write and triggers Spark
        execution. Depending on the selected mode, it may append to, create,
        replace, or overwrite Warehouse data according to the implementation
        and connector semantics. Supplying ``repartition_by`` triggers a Spark
        shuffle before the Warehouse transfer.

    Examples
    --------
    Small dimension table without explicit repartitioning:

    >>> write_warehouse_table(
    ...     department_lookup_df,
    ...     "dbo",
    ...     "DIM_DEPARTMENT",
    ...     target="warehouse",
    ...     mode="overwrite",
    ... )

    A small dimension or lookup table usually does not require repartitioning.
    Adding many partitions to a small DataFrame can increase overhead without
    improving the write.

    Integer repartitioning for a large fact dataset:

    >>> write_warehouse_table(
    ...     large_fact_df,
    ...     "dbo",
    ...     "FACT_STUDENT_ENROLMENT",
    ...     target="warehouse",
    ...     mode="append",
    ...     repartition_by=32,
    ... )

    Column-based repartitioning:

    >>> write_warehouse_table(
    ...     large_fact_df,
    ...     "dbo",
    ...     "FACT_STUDENT_ENROLMENT",
    ...     target="warehouse",
    ...     mode="append",
    ...     repartition_by=["academic_year", "semester"],
    ... )

    Large fact dataset pattern:

    >>> write_warehouse_table(
    ...     transaction_df,
    ...     "dbo",
    ...     "FACT_TRANSACTIONS",
    ...     target="warehouse",
    ...     mode="append",
    ...     repartition_by=48,
    ... )

    The value ``48`` is illustrative. The correct value depends on DataFrame
    size, existing partitions, skew, executor capacity, connector behaviour,
    and Warehouse ingestion limits.

    """
    validate_dataframe_writer(df)
    df = repartition_dataframe_for_write(df, repartition_by)
    if load_strategy in {"scd1", "scd2"}:
        if mode is not None:
            raise ValueError(f"mode must be None when load_strategy is {load_strategy}.")
        execute_warehouse_processing(
            df,
            schema=schema,
            table_name=table_name,
            target=target,
            processing={"load_strategy": load_strategy, **(load_strategy_parameters or {})},
            context=context,
            options=options,
        )
    else:
        store, _schema_value, _table_value, object_name = resolve_configured_warehouse_table(
            target, schema, table_name, context=context
        )
        write_warehouse_synapsesql(df, store, object_name, mode=mode, options=options)
    if completion_context is not None:
        from fabricops_kit.pipeline.shared import complete_source_processing

        complete_source_processing(completion_context, context=context)
