# `write_incremental_lakehouse_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Apply overwrite, append, merge/SCD1, or SCD2 to a Lakehouse Delta target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_incremental_lakehouse_table.py:70`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/write_incremental_lakehouse_table.py#L70-L178">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_incremental_lakehouse_table(
    df,
    table_name: str,
    plan: dict,
    target: str='target',
    schema: str | None=None,
    tracked_columns: list[str] | tuple[str, ...] | None=None,
    spark_session=None,
    context: dict[str, Any] | None=None,
) -> None:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> write_incremental_lakehouse_table(transformed, "orders", plan, target="curated")

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Transformed and validated rows in the read scope selected by ``plan``. |
| `table_name` | `str` | Yes | Configured target Lakehouse table name. |
| `plan` | `dict` | Yes | Result returned by :func:`plan_incremental_processing`. |
| `target` | `str` | No | Logical Lakehouse target from ``00_env_config``. |
| `schema` | `str \| None` | No | Lakehouse schema, when schema support is enabled. |
| `tracked_columns` | `list[str] \| tuple[str, ...] \| None` | No | SCD2 business columns to compare. By default non-key, non-effective, non-technical, non-audit input columns are compared. |
| `spark_session` | `pyspark.sql.SparkSession` | No | Explicit Spark session; the active Fabric session is used by default. |
| `context` | `dict[str, Any] \| None` | No | Resolved FabricOps runtime context. |

## Returns

None.

## Raises / Errors

ValueError
    If plan fields, required columns, or key uniqueness are invalid.
RuntimeError
    If Delta Lake operations are unavailable in the runtime.

## Notes

<div class="reference-docstring-notes" markdown="1">

Merge implements current-state/SCD Type 1 upserts. SCD2 maintains
``valid_from``, ``valid_to``, and ``is_current`` and never infers deletes.

</div>

## See also

No related guides documented.


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |


</details>
