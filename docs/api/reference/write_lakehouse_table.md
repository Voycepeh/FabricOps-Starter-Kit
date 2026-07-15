# `write_lakehouse_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 17
- Shared helpers: 9
- Private helpers: 8

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=write_lakehouse_table">Open Live contract call flow</a>

Write a Spark DataFrame to a configured Fabric lakehouse Delta table.

<div class="reference-docstring-intro" markdown="1">

The function performs an immediate Spark write using the selected write
mode and optional execution and storage partitioning settings. Lakehouse
Delta is optimized for FabricOps PySpark processing and reuse. Prefer this
callable for repeated PySpark processing and reusable intermediate,
Unified, Product, and metadata Delta outputs that will be read repeatedly
by Spark. Publish selected serving outputs to Warehouse separately when
SQL serving is required.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_lakehouse_table.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_lakehouse_table.py#L15-L230">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
<span class="reference-chip">example_pipeline_demo</span>
<span class="reference-chip">example_dq_rule_smoke_test</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`, `example_pipeline_demo`, `example_dq_rule_smoke_test`

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_lakehouse_table(
    df,
    table_name: str,
    target: str='unified',
    schema=None,
    mode='append',
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose=True,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

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

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to write. |
| `table_name` | `str` | Yes | Lakehouse table name. Supply ``schema`` and ``table_name`` separately; do not pass a qualified name such as ``schema.table`` through ``table_name``. |
| `target` | `str` | No | Logical Lakehouse target from ``00_env_config``. FabricOps resolves the selected environment, workspace, Lakehouse item, optional schema, table name, and OneLake Delta path under the Lakehouse ``Tables`` area. |
| `schema` | `str or None` | No | Optional schema override for schema-enabled Lakehouses. |
| `mode` | `str, default="append"` | No | Spark Delta write mode. ``append`` adds rows to the existing destination or creates it when absent. Rerunning the same input can create duplicate rows. No business-key matching, deduplication, or idempotency check is performed. ``overwrite`` replaces the destination data according to Spark Delta writer behavior and should be treated as destructive. ``errorifexists`` fails when the destination already exists. ``ignore`` skips the write when the destination already exists. This function does not perform a Delta ``MERGE``, upsert, update-on-match, delete-on-missing, or key-based deduplication. |
| `partition_by` | `str or list[str]` | No | Column or columns used to create physical Delta table partitions in storage. Use this for stable, commonly filtered, relatively low-cardinality columns such as year or month when that layout improves downstream reads. ``partition_by`` affects the physical Delta table layout rather than Spark execution parallelism. High-cardinality partition columns can create excessive folders and small files, and the function does not inspect or reconcile an existing table's partition layout before writing. |
| `repartition_by` | `int, str, list, or tuple` | No | Optional repartitioning applied to the Spark DataFrame before the write. This changes the Spark partition distribution and can increase Spark write parallelism by creating additional partitions that Spark may process concurrently, subject to available cluster resources and destination throughput. Small DataFrames normally do not need explicit repartitioning. Large datasets, including workloads with millions of rows, may benefit when partition counts are tuned for data volume, row width, skew, file sizes, and available Fabric Spark capacity. Millions of rows is an example workload size rather than a hard threshold. Row count alone is not sufficient for tuning. Excessive repartitioning can add shuffle cost, scheduler overhead, and many small files. ``repartition_by=32`` is equivalent to ``df.repartition(32)``. ``repartition_by="department"`` is equivalent to ``df.repartition("department")``. ``repartition_by=["year", "month"]`` is equivalent to ``df.repartition("year", "month")``. ``repartition_by=(32, "year", "month")`` is equivalent to ``df.repartition(32, "year", "month")``. Repartitioning changes the DataFrame used for the write but does not mutate the caller's original DataFrame binding. |
| `options` | `dict` | No | Additional Spark Delta ``DataFrameWriter`` options forwarded before saving the configured Lakehouse ``Tables`` path, such as ``mergeSchema``, ``overwriteSchema``, and other standard Delta writer options supported by the active Spark runtime. FabricOps forwards these options and does not validate their compatibility. |
| `verbose` | `bool, default=True` | No | Whether to print the resolved output path before writing. |
| `context` | `dict[str, Any]` | No | Active Fabric context override. |

## Returns

None; the DataFrame is written to the configured Lakehouse Delta table path.

### Return interpretation

No value is returned; successful completion means the configured Lakehouse write was submitted.

## Raises / Errors

Raises ValueError for unsafe names, invalid write modes, or non-lakehouse targets.

### Common failure causes

- Guardrails were skipped before a target write.
- The target lakehouse is not configured for the environment.
- The write mode is unsupported for the destination.
- The caller lacks write permission or Spark cannot create the table.

## Notes

<div class="reference-docstring-notes" markdown="1">

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
| Live-critical dependencies | 17 |

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
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.normalize_write_mode</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.validate_dataframe_writer</code></li>
<li><code>fabricops_kit.io.shared.write_delta_path</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 15 Jul 2026, 2:26 PM SGT
    Call-flow data generated: 14 Jul 2026, 9:32 PM SGT
