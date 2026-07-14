# `write_warehouse_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 15
- Shared helpers: 8
- Private helpers: 7

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=write_warehouse_table">Open Live contract call flow</a>

Write a DataFrame to a configured Fabric warehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_warehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_warehouse_table.py#L10-L141">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


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

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to publish. |
| `schema` | `str` | Yes | Warehouse schema name. |
| `table_name` | `str` | Yes | Warehouse table name. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `mode` | `str` | No | Spark writer mode supported by the Fabric connector. |
| `repartition_by` | `int, str, list, or tuple` | No | Optional repartitioning applied to the Spark DataFrame before the Fabric connector write. This controls Spark write parallelism and does not create a physically partitioned Warehouse table. Small serving tables normally do not need explicit repartitioning. Repartitioning can increase Spark write parallelism by creating additional partitions that Spark may process concurrently, subject to available cluster resources and destination throughput. Large publications, including workloads with millions of rows, may benefit when partition counts are tuned for data volume, row width, skew, available Spark resources, connector behavior, and Fabric capacity. Millions of rows is an example workload size rather than a hard threshold, and row count alone is not sufficient for tuning. Too many partitions may reduce performance. |
| `options` | `dict[str, Any] \| None` | No | Additional Fabric Warehouse Spark connector writer options. Required Fabric connector options are always set from ``00_env_config``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

None; the DataFrame is written to the configured warehouse table.

### Return interpretation

A successful write means the helper submitted the DataFrame write to the configured warehouse target; verify downstream table state for business checks.

## Raises / Errors

Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.

### Common failure causes

- The warehouse target is missing from configuration.
- The target table name or write mode is invalid.
- Warehouse connector support is unavailable.
- The caller lacks write permission.

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
| Live-critical dependencies | 15 |

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
<li><code>fabricops_kit.io.shared.resolve_configured_warehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.resolve_warehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.validate_dataframe_writer</code></li>
<li><code>fabricops_kit.io.shared.write_warehouse_synapsesql</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 15 Jul 2026, 1:23 AM SGT
    Call-flow data generated: 14 Jul 2026, 9:32 PM SGT
