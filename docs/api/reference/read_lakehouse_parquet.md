# read_lakehouse_parquet

## Call-flow summary

- Downstream callables: 18
- Shared helpers: 10
- Private helpers: 8

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_lakehouse_parquet">Open focused call flow in dashboard</a>


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

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)


!!! info "Generated reference freshness"
    Reference pages generated: 06 Jul 2026, 4:12 PM SGT
    Call-flow data generated: 06 Jul 2026, 4:08 PM SGT
