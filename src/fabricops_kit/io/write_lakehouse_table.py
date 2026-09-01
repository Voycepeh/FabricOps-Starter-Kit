"""Owner file for the ``write_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import (
    normalize_write_mode,
    repartition_dataframe_for_write,
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
    load_strategy=None,
    load_strategy_parameters=None,
    processing_scope=None,
    completion_context=None,
):
    """Write a Spark DataFrame to a configured Fabric lakehouse Delta table.

    ``write_lakehouse_table`` writes a Spark DataFrame to a Fabric lakehouse
    table using the configured FabricOps target, schema, table name, and write
    settings. It supports Spark-side repartitioning before the write so large
    datasets can be processed by multiple Spark tasks concurrently.

    The function also supports physical Delta table partitioning when
    ``partition_by`` is supplied. Spark execution repartitioning and Delta
    table partitioning solve different problems and should not be treated as
    interchangeable.

    Use this function after a pipeline DataFrame has been prepared and passed
    the required validation or guardrail checks. For small datasets, use the
    default write path without forcing repartitioning. For large datasets,
    including datasets containing millions of rows, use ``repartition_by``
    when additional Spark write parallelism is needed. Use ``partition_by``
    only when the persisted Delta table should be physically organized by
    stable, commonly filtered columns. Do not add physical partitions merely to
    make one write faster.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write. When ``repartition_by`` is provided, the
        function creates a repartitioned DataFrame for the write; it does not
        mutate the original DataFrame object.
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
    mode : {"append", "overwrite", "errorifexists", "ignore"}, default="append"
        Controls how the target table is written. ``append`` adds rows,
        ``overwrite`` may replace existing table data and should be selected
        explicitly, ``errorifexists`` fails when the destination exists, and
        ``ignore`` skips the write when the destination exists.
    partition_by : str or list[str] or tuple[str, ...], optional
        Optional column name or collection of columns used to physically
        partition the persisted Delta table. This controls the table's stored
        layout and is separate from Spark execution repartitioning. Use columns
        with appropriate cardinality and stable downstream filtering value.
    repartition_by : int or str or list[str] or tuple[str, ...], optional
        Optional Spark repartitioning instruction applied immediately before
        the write. A positive integer controls the number of Spark execution
        partitions. A column name or collection of column names redistributes
        rows by those keys. A list or tuple beginning with a positive integer
        supplies both the partition count and the distribution columns.
        Repartitioning triggers a shuffle and should be used deliberately for
        large, under-partitioned, or skewed datasets.
    options : dict, optional
        Additional Spark Delta ``DataFrameWriter`` options passed to the
        underlying write operation, such as ``mergeSchema`` or
        ``overwriteSchema`` where supported by the active Spark runtime.
        FabricOps forwards these options and does not claim schema evolution
        unless the supplied Spark/Delta option supports it.
    verbose : bool, default=True
        Whether to print the resolved output path before writing.
    context : dict[str, Any], optional
        Active Fabric context override.
    load_strategy : {"overwrite", "append", "scd1", "scd2"}, optional
        Governed target-maintenance strategy returned by
        :func:`write_pipeline_prep`. For SCD strategies, ``mode`` must be
        ``None`` because the physical action is a Delta merge, not an append.
    load_strategy_parameters : dict, optional
        Governed strategy parameters returned by :func:`write_pipeline_prep`.
    processing_scope : dict, optional
        Prepared skip, full, or incremental execution scope.
    completion_context : dict, optional
        Governed source-completion context returned by
        :func:`write_pipeline_prep`. When supplied, source progress is
        committed only after the physical write succeeds. The target Lineage
        participant is persisted before source progress. Calls that omit it
        have no Lineage or checkpoint effects.

    Returns
    -------
    None
        The function performs the Spark Delta write before returning.

    Notes
    -----
    Governed completion
        When ``completion_context`` is supplied, the physical target write or
        merge completes first and source progress is committed second. A
        physical-write exception prevents the commit. If checkpoint
        persistence fails after publication, that exception is surfaced and a
        retry may replay already-published source rows; the target load
        strategy remains responsible for deterministic replay semantics.

    Parallel processing and write concurrency
        Spark writes DataFrame partitions concurrently across available
        executors. ``write_lakehouse_table`` can repartition the input
        DataFrame before writing, allowing the caller to influence how many
        Spark tasks participate in the write and how records are distributed
        between those tasks.

        This is distributed Spark execution, not Python thread-level
        concurrency. The function does not start multiple Python writers and
        does not submit the same table write several times.

        Repartitioning can improve throughput when the existing DataFrame has
        too few partitions, poorly distributed partitions, or severe data
        skew. It also introduces a Spark shuffle, so increasing the partition
        count does not automatically make every write faster.

    Integer repartitioning
        Passing a positive integer to ``repartition_by`` redistributes the
        DataFrame into that number of Spark partitions before writing by
        calling ``df.repartition(number)``. Spark can then schedule up to that
        many partition-writing tasks, subject to available executor capacity
        and Spark/Delta writer behaviour.

    Column-based repartitioning
        Passing a column name, string-only list, or string-only tuple repartitions
        the DataFrame by the selected values before writing by calling
        ``df.repartition(*columns)``.
        Rows with the same partitioning key are routed consistently according
        to Spark's hash partitioning. Column-based repartitioning can help
        distribute a large write using meaningful keys, but low-cardinality or
        heavily skewed keys can create unbalanced partitions. This does not
        physically partition the stored Delta table unless ``partition_by`` is
        also supplied. A list or tuple such as ``(32, "academic_year",
        "semester")`` calls ``df.repartition(32, "academic_year",
        "semester")`` and controls both Spark task count and distribution keys
        for the current write.

    Repartitioning versus physical Delta partitioning

        | Setting | Affects | Purpose | Persisted in table layout |
        | --- | --- | --- | --- |
        | ``repartition_by`` | Spark DataFrame before writing | Controls task parallelism and row distribution during the write | No |
        | ``partition_by`` | Delta table files and folders | Organizes stored data by selected columns for pruning and maintenance | Yes |

        ``repartition_by`` changes the DataFrame's Spark execution partitions
        before the write. It affects how Spark performs the current operation
        but does not define the long-term physical partition columns of the
        Delta table.

        ``partition_by`` defines the physical Delta table partition layout. It
        should be selected based on query patterns, cardinality, data volume,
        and file-management considerations rather than being used as a general
        concurrency switch.

        Both options may be used together when the execution distribution and
        persisted Delta layout intentionally serve different requirements.

    Implementation sequence
        The function validates the DataFrame writer, validates the table
        identity and write mode, resolves the lakehouse target and optional
        schema, validates ``repartition_by``, calls ``df.repartition(number)``
        for a positive integer, ``df.repartition(*columns)`` for a column
        name/list/tuple, or ``df.repartition(number, *columns)`` when a list or
        tuple begins with a positive integer, passes the resulting DataFrame to
        the Delta writer,
        applies ``partition_by`` only to the physical Delta write
        configuration, executes the selected write mode, and returns ``None``.

    Performance notes
        The existing number of DataFrame partitions may already be
        appropriate. Check the workload before forcing repartitioning. Too few
        partitions can underuse available Spark executors and produce very
        large individual write tasks. Too many partitions can increase shuffle
        overhead and create excessive small files. Repartitioning by a skewed
        column may concentrate a large proportion of records in only a few
        tasks. Physical Delta partitioning with high-cardinality columns can
        create excessive directories and small files. Repartitioning improves
        the opportunity for concurrent Spark task execution but does not
        override cluster capacity, lakehouse service limits, locking
        behaviour, or concurrent-operation constraints.

    Errors and edge cases
        ``repartition_by`` rejects zero or negative integers, missing columns
        when DataFrame columns are available, unsupported types, empty lists or
        tuples, and non-string column values after any leading partition count. Invalid ``partition_by`` columns, schema mismatch,
        append-versus-overwrite conflicts, insufficient permissions,
        concurrent writes to the same target table, partial or failed Delta
        commits, empty DataFrames, small-file risk, and Spark shuffle failures
        are handled by Spark/Delta or the configured Fabric runtime. The
        function does not make simultaneous independent writes to the same
        table safe.

    Side effects
        This function performs a physical Delta table write and triggers Spark
        execution. Depending on the selected mode, it may create, append to,
        replace, or overwrite the target table. ``repartition_by`` triggers a
        shuffle before the write. ``partition_by`` affects the persisted Delta
        layout.

    Examples
    --------
    Small lookup table without explicit repartitioning:

    >>> write_lakehouse_table(
    ...     small_lookup_df,
    ...     "COUNTRY_REGION_MAPPING",
    ...     target="data",
    ...     schema=DATA_SCHEMA,
    ...     mode="overwrite",
    ... )

    A small lookup table generally does not need explicit repartitioning.
    Forcing many Spark partitions for a small dataset can create unnecessary
    shuffle work and many small output files.

    Integer repartitioning for a large dataset:

    >>> write_lakehouse_table(
    ...     large_df,
    ...     "STUDENT_ENROLMENT_CURATED",
    ...     target="data",
    ...     schema=DATA_SCHEMA,
    ...     mode="overwrite",
    ...     repartition_by=32,
    ... )

    The DataFrame is shuffled into 32 Spark partitions before the Delta write.
    This is appropriate only when the dataset is large enough to benefit from
    additional parallel tasks.

    Column-based repartitioning:

    >>> write_lakehouse_table(
    ...     large_df,
    ...     "STUDENT_ENROLMENT_CURATED",
    ...     target="data",
    ...     schema=DATA_SCHEMA,
    ...     mode="overwrite",
    ...     repartition_by=["academic_year", "semester"],
    ... )

    Combined Spark repartitioning and physical Delta partitioning:

    >>> write_lakehouse_table(
    ...     large_df,
    ...     "STUDENT_ENROLMENT_CURATED",
    ...     target="data",
    ...     schema=DATA_SCHEMA,
    ...     mode="overwrite",
    ...     repartition_by=32,
    ...     partition_by=["academic_year"],
    ... )

    Here, Spark first creates 32 execution partitions to distribute the write
    work. The resulting Delta table is physically partitioned by
    ``academic_year``. The number of Spark execution partitions is not the same
    thing as the number of physical table partition values.

    Large historical dataset pattern:

    >>> write_lakehouse_table(
    ...     enrolment_df,
    ...     "STUDENT_ENROLMENT_HISTORY",
    ...     target="data",
    ...     schema=DATA_SCHEMA,
    ...     mode="overwrite",
    ...     repartition_by=48,
    ...     partition_by=["academic_year"],
    ... )

    This pattern is intended for a large historical dataset containing millions
    of rows. The value ``48`` is an example, not a universal recommendation.

    """
    validate_dataframe_writer(df)
    if load_strategy is not None:
        if processing_scope is None:
            raise ValueError("processing_scope is required with load_strategy.")
        strategy = str(load_strategy).strip().lower()
        if strategy in {"scd1", "scd2"}:
            if mode is not None:
                raise ValueError("mode must be None for governed SCD execution; SCD strategies use Delta merge semantics.")
            from fabricops_kit.pipeline.shared import execute_lakehouse_processing

            execute_lakehouse_processing(
                df, table_name=table_name, target=target, schema=schema,
                processing={"load_strategy": strategy, **(load_strategy_parameters or {})},
                scope=processing_scope, context=context,
            )
            if completion_context is not None:
                from fabricops_kit.pipeline.shared import complete_source_processing

                complete_source_processing(completion_context, context=context)
            return
        if strategy not in {"overwrite", "append"} or mode != strategy:
            raise ValueError("Governed overwrite/append load_strategy must match the physical writer mode.")
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        target, table_name, schema, context=context
    )
    normalized_mode = normalize_write_mode(mode)
    df = repartition_dataframe_for_write(df, repartition_by)
    if verbose:
        print(f"Writing Lakehouse table to {path}")
    write_delta_path(df, path, mode=normalized_mode, partition_by=partition_by, options=options)
    if completion_context is not None:
        from fabricops_kit.pipeline.shared import complete_source_processing

        complete_source_processing(completion_context, context=context)
