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

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_table.py#L10-L56">View on GitHub</a>
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
df_orders = read_lakehouse_table("orders", target="source", schema=SOURCE_SCHEMA, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `schema` | `str \| None` | No | Optional schema override for schema-enabled lakehouses. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark Delta reader options forwarded to ``DataFrameReader``. |

## Returns

Spark DataFrame loaded from the configured Lakehouse Delta table path.

### Return interpretation

The returned DataFrame represents the resolved Lakehouse table.

## Raises / Errors

Raises ValueError for unsafe names or non-lakehouse targets and RuntimeError when Spark is unavailable.

### Common failure causes

- The target or table name is misspelled.
- The selected environment does not define the requested lakehouse target.
- Spark cannot access the table.
- The caller lacks permission to read the lakehouse.

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
    Reference pages generated: 12 Jul 2026, 12:52 PM SGT
    Call-flow data generated: 12 Jul 2026, 12:50 PM SGT
