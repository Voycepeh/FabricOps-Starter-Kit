# `write_warehouse_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 16
- Shared helpers: 9
- Private helpers: 7

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=write_warehouse_table">Open Live contract call flow</a>

Write a DataFrame to a configured Fabric warehouse target.

<div class="reference-docstring-intro" markdown="1">

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

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_warehouse_table.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_warehouse_table.py#L15-L244">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Usage notes

Parallel Spark tasks within one write_warehouse_table call are not the same as several notebooks or jobs writing to the same Warehouse table concurrently. The function does not coordinate independent writers or guarantee safe simultaneous overwrite operations, and it must not be documented with lakehouse-style partition_by behaviour.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_warehouse_table(
    df,
    schema: str,
    table_name: str,
    target: str='warehouse',
    mode: str='append',
    repartition_by=None,
    options: dict[str, Any] | None=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

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

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to transfer into the Warehouse. The original DataFrame object is not modified; a repartitioned DataFrame is used for the write when requested. |
| `schema` | `str` | Yes | Warehouse schema containing the target table, such as ``dbo``. This is part of the Warehouse object identity and is unrelated to Spark schema inference. |
| `table_name` | `str` | Yes | Warehouse table name. |
| `target` | `str` | No | Logical Warehouse target from ``00_env_config``. FabricOps resolves the logical target, workspace ID, Warehouse item ID, Warehouse database name, schema, and table name. |
| `mode` | `str` | No | Requested Warehouse write behaviour passed to the Fabric Warehouse Spark connector. ``append`` adds rows and can duplicate repeated publications. ``overwrite`` requests replacement behaviour and should be treated as destructive. Other supported modes are passed through to Spark/connector semantics. |
| `repartition_by` | `int or str or list[str] or tuple[str, ...]` | No | Optional Spark-side repartitioning applied before the Warehouse connector is invoked. A positive integer controls the number of Spark execution partitions. A column name or collection of column names redistributes records by those keys. A list or tuple beginning with a positive integer supplies both the partition count and the distribution columns. This controls Spark processing for the current write and does not configure the Warehouse table's physical design. |
| `options` | `dict[str, Any] \| None` | No | Additional Fabric Warehouse Spark connector writer options. FabricOps sets the resolved Workspace ID and Warehouse item ID before applying caller options, then forwards caller options to the connector writer. Do not pass custom options that replace the resolved destination identity settings. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

None. The function validates repartitioning, optionally writes a repartitioned DataFrame through the Warehouse connector, and returns after connector execution completes or raises an error.

### Return interpretation

A successful write means the helper submitted the DataFrame write to the configured warehouse target; verify downstream table state for business checks.

## Raises / Errors

Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.

### Common failure causes

- Zero or negative repartition counts, missing repartition columns, unsupported repartition_by value types, empty lists/tuples, or non-string column values after any leading partition count.
- Schema or table not found, unsupported write mode, authentication or connector failure, Warehouse permission failure, or unsupported Spark-to-Warehouse type conversion.
- Connector-managed transfer or staging failure, transaction or lock conflict, empty DataFrame behaviour, large transfer timeout/resource exhaustion, or accidentally writing the original DataFrame instead of the repartitioned one.

## Notes

<div class="reference-docstring-notes" markdown="1">

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

</div>

## See also

- [Templates](../../notebook-templates-implementation-guide/index.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 16 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.io.shared._build_warehouse_object_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._require_fabric_connector</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.repartition_dataframe_for_write</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_warehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.validate_dataframe_writer</code></li>
<li><code>fabricops_kit.io.shared.write_warehouse_synapsesql</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 16 Jul 2026, 1:51 PM SGT
    Call-flow data generated: 16 Jul 2026, 12:56 AM SGT
