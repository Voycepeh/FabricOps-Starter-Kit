# `read_lakehouse_query`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.4.2</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Run read-only Spark SQL against one configured Lakehouse table.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Use when selecting or filtering one configured Lakehouse table with Spark SQL.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_query("SELECT TOP (5) order_id FROM demo.orders", table_name="orders", schema="demo", store="Bronze")
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_query(
    query: str,
    *,
    table_name: str,
    store: str='Bronze',
    schema: str | None=None,
    context: dict[str, Any] | None=None,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `query` | `str` | Yes | `—` | One read-only Spark SQL SELECT or CTE referencing the declared source. Simple integer T-SQL TOP projections are also supported. |
| `table_name` | `str` | Yes | `—` | Required Lakehouse table name referenced by the query. Supply its schema separately with ``schema``. |
| `store` | `str` | No | `'Bronze'` | Logical Lakehouse store key configured in ``00_env_config``. |
| `schema` | `str \| None` | No | `None` | Schema for the declared source in a schema-enabled Lakehouse. |
| `context` | `dict[str, Any] \| None` | No | `None` | Active Fabric context override containing an existing Spark session and configured Lakehouse routing. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_query(
    "SELECT TOP (5) order_id FROM demo.orders",
    table_name="orders", schema="demo", store="Bronze",
)
```

</div>

## Returns

pyspark.sql.DataFrame
    Lazy query result bound to the configured physical source. A downstream
    Spark action evaluates the data.

### Return interpretation

The DataFrame represents the bound query; downstream Spark actions evaluate its data.

## Raises / Errors

ValueError
    If the declared source is invalid, SQL is not read-only, another source
    is referenced, or unsupported T-SQL cannot be converted safely.
RuntimeError
    If no active Spark session or configured Lakehouse target is available.

### Common failure causes

- The query references a different physical source.
- T-SQL uses unsupported constructs.
- The Lakehouse target is not configured or readable.
- No active Spark session is available.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

The query must reference the declared table (or schema.table). CTEs,
filters, projections, aggregations and self-joins use Spark SQL.
Simple T-SQL integer TOP projections are translated to LIMIT; unsupported
T-SQL fails rather than silently changing semantics.

The source is bound through the configured physical Lakehouse location,
including cross-workspace stores, not the Spark session's default catalog.
No pipeline setup, metadata mutation, or contract enforcement is performed.

Returns a Spark DataFrame. No Spark session is created.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_query.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_query.py#L10-L89">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.4.2 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 20 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_owner</code></li>
<li><code>fabricops_kit.config.metadata_schemas.metadata_table_physical_schema</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
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
<li><code>fabricops_kit.io.shared.resolve_configured_lakehouse_table</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_table_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
<li><code>fabricops_kit.pipeline.pipeline_read._lakehouse_query</code></li>
</ul>


</details>
