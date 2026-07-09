# `read_lakehouse_csv`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 15
- Shared helpers: 9
- Private helpers: 6

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_lakehouse_csv">Open Live contract call flow</a>

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
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_csv_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
</ul>


Read a CSV file from a configured Fabric-resolved path through Spark CSV.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_csv.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_csv.py#L10-L49">View on GitHub</a>
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
def read_lakehouse_csv(
    relative_path: str,
    target: str='source',
    spark_session=None,
    header: bool=True,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_csv(relative_path="raw/orders/orders.csv", header=True, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | CSV file or folder path resolved by the Fabric resolver. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `header` | `bool` | No | Whether the first row contains column names. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark CSV reader options forwarded to Spark's CSV reader. |

## Returns

Spark DataFrame loaded from the Fabric-resolved CSV path.

### Return interpretation

The returned DataFrame reflects Spark CSV parsing options; inspect schema and sample rows before profiling or writing.

## Raises / Errors

Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.

### Common failure causes

- The file path is wrong or outside the configured Fabric target.
- CSV options do not match the file shape.
- Spark cannot access the file.
- The selected environment is missing the source lakehouse target.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)


!!! info "Generated reference freshness"
    Reference pages generated: 09 Jul 2026, 11:26 PM SGT
    Call-flow data generated: 09 Jul 2026, 8:52 PM SGT
