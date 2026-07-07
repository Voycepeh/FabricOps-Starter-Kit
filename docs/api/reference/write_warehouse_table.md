# write_warehouse_table

## Call-flow summary

- Downstream callables: 15
- Shared helpers: 8
- Private helpers: 7

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=write_warehouse_table">Open focused call flow in dashboard</a>


Write a DataFrame to a configured Fabric warehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_warehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_warehouse_table.py#L10-L63">View on GitHub</a>
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
    options: dict[str, Any] | None=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
write_warehouse_table(serving_df, target="Warehouse", schema="dbo", table="orders_serving", mode="append")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to publish. |
| `schema` | `str` | Yes | Warehouse schema name. |
| `table_name` | `str` | Yes | Warehouse table name. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `mode` | `str` | No | Spark writer mode supported by the Fabric connector. |
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

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)


!!! info "Generated reference freshness"
    Reference pages generated: 07 Jul 2026, 10:14 PM SGT
    Call-flow data generated: 07 Jul 2026, 10:14 PM SGT
