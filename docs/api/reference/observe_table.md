# `observe_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Cheaply identify changed table partitions before expensive source work.

<div class="reference-docstring-intro" markdown="1">

``observe_table()`` cheaply records row count and latest change value by
source partition so FabricOps can decide whether more expensive source
processing is required.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/observe_table.py:137`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/observe_table.py#L137-L293">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def observe_table(
    table_name: str,
    target: str='source',
    schema: str | None=None,
    partition_column: str,
    change_column: str,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> plan = observe_table(
...     table_name="orders",
...     target="source",
...     schema="dbo",
...     partition_column="business_date",
...     change_column="modified_at",
... )
>>> plan["requires_read"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Table name within the configured target. |
| `target` | `str` | No | Logical Lakehouse or Warehouse target configured by ``00_env_config``. |
| `schema` | `str \| None` | No | Optional Lakehouse schema. A schema is required for Warehouse targets. |
| `partition_column` | `str` | Yes | Column whose distinct values identify independently readable partitions. |
| `change_column` | `str` | Yes | Trustworthy column that advances when rows in a partition are inserted or updated, such as ``modified_at``, ``updated_at``, or ``last_changed_at``. |

## Returns

Compact observations plus changed and new partitions and a restricted read predicate.

## Raises / Errors

ValueError
    If table identity, columns, target type, or a required Warehouse schema
    is invalid.
RuntimeError
    If ``00_env_config`` has not initialized FabricOps or observation
    history cannot be read.

## Notes

<div class="reference-docstring-notes" markdown="1">

The stored evidence is only the partition, row count, and latest change
value. This is a lightweight change signal, not proof that every cell is
unchanged. Sources without a reliable change column require deeper change
detection elsewhere. Warehouse aggregation is pushed into SQL; Lakehouse
aggregation is distributed and projects only the two required columns.
Compact history and removal tombstones are appended to the configured
FabricOps metadata Lakehouse.

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
