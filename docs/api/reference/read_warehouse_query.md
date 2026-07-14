# `read_warehouse_query`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 12
- Shared helpers: 8
- Private helpers: 4

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_warehouse_query">Open Live contract call flow</a>

Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_warehouse_query.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_warehouse_query.py#L15-L74">View on GitHub</a>
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
def read_warehouse_query(
    query: str,
    target: str='warehouse',
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_warehouse_query("SELECT order_id, status FROM dbo.orders WHERE status = 'OPEN'", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | `str` | Yes | SQL ``SELECT`` statement, or a CTE beginning with ``WITH`` and ending in a ``SELECT``, to execute through the Fabric warehouse connector. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Fabric Warehouse Spark connector reader options. Required Fabric connector options are always set from ``00_env_config``. |

## Returns

Spark DataFrame returned by the Fabric warehouse connector.

### Return interpretation

The returned DataFrame contains the query result from the warehouse SQL serving engine.

## Raises / Errors

Raises ValueError for blank or non-SELECT SQL and RuntimeError when the Fabric connector is unavailable.

### Common failure causes

- The SQL is blank or not a SELECT/CTE.
- The warehouse target is not configured.
- The Fabric connector is unavailable.
- The caller lacks warehouse read permission.

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
| Live-critical dependencies | 12 |

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
<li><code>fabricops_kit.io.shared._require_fabric_connector</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_warehouse_synapsesql</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_warehouse_query_target</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
<li><code>fabricops_kit.io.shared.validate_select_query</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 14 Jul 2026, 5:03 PM SGT
    Call-flow data generated: 14 Jul 2026, 5:02 PM SGT
