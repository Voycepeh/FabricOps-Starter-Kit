<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `write_warehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.io.write_warehouse_table.write_warehouse_table`

Source path: `src/fabricops_kit/io/write_warehouse_table.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/io/write_warehouse_table.py)

Signature: `write_warehouse_table(df, schema: 'str', table_name: 'str', *, target: 'str' = 'warehouse', mode: 'str' = 'append', repartition_by=None, options: 'dict[str, Any] | None' = None, context: 'dict[str, Any] | None' = None)`

## Description

Write a Spark DataFrame to a configured Fabric Warehouse table.

## Parameters

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

## Return value

None
    The function performs the Fabric Warehouse connector write before
    returning.

## Usage notes

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
    ``None``. The current implementation delegates transfer to the Fabric
    Warehouse Spark connector through ``synapsesql`` and does not implement
    a separate temporary staging cleanup step.

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

Side effects
    This function performs a physical Warehouse write and triggers Spark
    execution. Depending on the selected mode, it may append to, create,
    replace, or overwrite Warehouse data according to the implementation
    and connector semantics. Supplying ``repartition_by`` triggers a Spark
    shuffle before the Warehouse transfer.

[Back to release overview](../index.md)
