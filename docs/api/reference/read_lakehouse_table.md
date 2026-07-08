# read_lakehouse_table

## Call-flow summary

- Downstream callables: 16
- Shared helpers: 8
- Private helpers: 8

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_lakehouse_table">Open focused call flow in dashboard</a>


Read a Delta table from a configured Fabric lakehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_table.py#L10-L56">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

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

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)


!!! info "Generated reference freshness"
    Reference pages generated: 08 Jul 2026, 1:08 PM SGT
    Call-flow data generated: 08 Jul 2026, 1:07 PM SGT
