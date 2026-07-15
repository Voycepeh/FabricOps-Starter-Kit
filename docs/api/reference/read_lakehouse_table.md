# `read_lakehouse_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 16
- Shared helpers: 8
- Private helpers: 8

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_lakehouse_table">Open Live contract call flow</a>

Read a Delta table from a configured Fabric lakehouse target.

<div class="reference-docstring-intro" markdown="1">

This function represents a complete read of the resolved Delta table and
returns all rows and columns in that table. It does not automatically
filter rows, select a subset of columns, aggregate data, apply a row
limit, or sample the data. It is conceptually similar to a full-table read
such as ``SELECT * FROM schema.table_name``, but the implementation
resolves the Lakehouse Delta path and uses Spark's Delta reader rather than
executing SQL.

The returned Spark DataFrame is lazy. Calling ``read_lakehouse_table``
constructs the DataFrame plan, and Spark reads data only when a downstream
action executes, such as ``display``, ``count``, ``collect``, or a
DataFrame write. Subsequent Spark transformations may still allow Delta
column pruning and predicate pushdown during execution.

Lakehouse Delta is the preferred source for repeated PySpark
transformations in FabricOps. Use this callable for managed Lakehouse
tables, data already materialized into OneLake Delta format, and source or
unified data processing inside Fabric notebooks. When source data starts in
a Fabric Warehouse, materialize large or repeatedly used data into the
Source Lakehouse as Delta first, then read it with this callable.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_table.py#L10-L100">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_table(
    table_name: str,
    target: str='source',
    schema: str | None=None,
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
catalogue_df = read_lakehouse_table("METADATA_DATA_CATALOGUE", target="metadata", schema=METADATA_SCHEMA, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. |
| `target` | `str` | No | Logical Lakehouse target from ``00_env_config``, such as ``source`` or ``unified``. FabricOps resolves this target to the configured physical Lakehouse and Delta table path. |
| `schema` | `str \| None` | No | Optional schema override for schema-enabled Lakehouses. Supply it separately from ``table_name``: use ``schema="sales"`` and ``table_name="orders"`` rather than ``table_name="sales.orders"``. This is normally omitted for Lakehouses without schemas. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark Delta ``DataFrameReader`` options forwarded to the Delta reader. These options do not provide FabricOps-level filtering or projection. |

## Returns

Spark DataFrame containing the current rows and columns of the resolved lakehouse table. The DataFrame preserves the table Spark schema and remains lazy until an action is executed.

### Return interpretation

The returned DataFrame represents the resolved Lakehouse table.

## Raises / Errors

Raises ValueError for unsafe names or non-lakehouse targets and RuntimeError when Spark is unavailable.

### Common failure causes

- The target cannot be resolved or is not a lakehouse.
- The table is not found, exists under another lakehouse or schema, or the schema argument is incorrect.
- The caller lacks read permissions or no Spark session is available.
- Spark Delta read failures may be deferred until an action evaluates the DataFrame.

## Notes

<div class="reference-docstring-notes" markdown="1">

FabricOps resolves the configured Lakehouse Tables path from
``00_env_config`` and then delegates to Spark's Delta reader with any
supplied reader options. Filtering and column selection are applied later
through normal Spark DataFrame operations. Conceptual examples:

``df = read_lakehouse_table(table_name="orders", target="source")``

``df = read_lakehouse_table(table_name="orders", target="source", schema="sales")``

``orders_df = read_lakehouse_table(table_name="sales_orders", target="source")``

``recent_orders_df = orders_df.select("order_id", "customer_id", "order_date", "amount").where("order_date >= '2026-01-01'")``

``read_lakehouse_table`` itself does not accept filtering or projection
arguments, but Spark may push compatible downstream filters and
projections into the Delta scan during execution.

This function does not read through the Warehouse SQL connector, execute a
SQL query, write or copy the table, register metadata, create the table,
mutate the source table, or automatically cache or persist the returned
DataFrame.

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
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._normalize_schema_name</code></li>
<li><code>fabricops_kit.io.shared._normalize_table_name</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_schema</code></li>
<li><code>fabricops_kit.io.shared._resolve_lakehouse_table_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_delta_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 15 Jul 2026, 11:42 PM SGT
    Call-flow data generated: 15 Jul 2026, 11:41 PM SGT
