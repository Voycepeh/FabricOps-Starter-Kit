# write_lakehouse_table

## Call-flow summary

- Downstream callables: 17
- Shared helpers: 9
- Private helpers: 8

<a class="reference-source-link" href="../../assets/public-function-call-flows-dashboard.html?function=write_lakehouse_table">Open focused call flow in dashboard</a>


Write a Spark DataFrame to a configured Fabric lakehouse Delta table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_lakehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_lakehouse_table.py#L10-L57">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">example_pipeline_demo</span>
<span class="reference-chip">example_dq_rule_smoke_test</span>
</p>

**Used in notebooks:** `02_pipeline`, `example_pipeline_demo`, `example_dq_rule_smoke_test`

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

```python
write_lakehouse_table(df_orders, "orders_clean", target="unified", schema=UNIFIED_SCHEMA, mode="overwrite")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to write. |
| `table_name` | `str` | Yes | Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `schema` | `str or None` | No | Optional schema override for schema-enabled lakehouses. |
| `mode` | `str, default="append"` | No | Spark write mode: ``append``, ``overwrite``, ``errorifexists``, or ``ignore``. |
| `partition_by` | `str or list[str]` | No | Column or columns used to physically partition the Delta table. |
| `repartition_by` | `int, str, list, or tuple` | No | Optional repartitioning before write. |
| `options` | `dict` | No | Additional Spark DataFrameWriter options. |
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

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
