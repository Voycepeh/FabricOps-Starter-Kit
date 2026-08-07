<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `write_lakehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.io.write_lakehouse_table.write_lakehouse_table`

Source path: `src/fabricops_kit/io/write_lakehouse_table.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/io/write_lakehouse_table.py)

Signature: `write_lakehouse_table(df, table_name: 'str', *, target: 'str' = 'unified', schema=None, mode='append', partition_by=None, repartition_by=None, options=None, verbose=True, context=None)`

## Description

Write a Spark DataFrame to a configured Fabric lakehouse Delta table.

## Parameters

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

## Return value

None
    The function performs the Spark Delta write before returning.

## Usage notes

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

[Back to release overview](../index.md)
