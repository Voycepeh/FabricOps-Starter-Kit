# `read_lakehouse_parquet`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 18
- Shared helpers: 10
- Private helpers: 8

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_lakehouse_parquet">Open Live contract call flow</a>

Read a Parquet path from a configured Fabric-resolved path through Spark Parquet.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_parquet.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_parquet.py#L15-L119">View on GitHub</a>
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
def read_lakehouse_parquet(
    relative_path: str,
    target: str='source',
    verbose: bool=True,
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_parquet(relative_path="raw/orders/orders.parquet", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | Parquet file path resolved by the Fabric resolver. Root-level files such as ``customers.parquet`` and nested paths such as ``input/customers.parquet`` are supported. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `verbose` | `bool` | No | Whether to print read and timestamp-conversion fallback progress. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark Parquet reader options forwarded to every original and timestamp-converted fallback read attempt. |

## Returns

Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.

### Return interpretation

The returned DataFrame uses the Parquet schema read by Spark; validate it before downstream profile or guardrail checks.

## Raises / Errors

Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.

### Common failure causes

- The Parquet path is missing or misspelled.
- The file is not valid Parquet.
- The configured lakehouse target is unavailable.
- The caller lacks read permission.

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
| Live-critical dependencies | 14 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_relative_path</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.convert_single_parquet_ns_to_us</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 12 Jul 2026, 12:52 PM SGT
    Call-flow data generated: 12 Jul 2026, 12:50 PM SGT
