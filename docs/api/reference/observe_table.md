# `observe_table`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Record compact count and change-value bounds before expensive source work.

<div class="reference-docstring-intro" markdown="1">

``observe_table()`` cheaply records row count plus earliest and latest
change values by source partition so
later guardrail checks can judge the source without a full source read.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/observe_table.py:142`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/observe_table.py#L142-L287">View on GitHub</a>
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
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> observation_df = observe_table(
...     table_name="orders",
...     target="source",
...     schema="dbo",
... )
>>> observation_df.select("partition_value", "row_count")

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Table name within the configured target. |
| `target` | `str` | No | Logical Lakehouse or Warehouse target configured by ``00_env_config``. |
| `schema` | `str \| None` | No | Optional Lakehouse schema. A schema is required for Warehouse targets. |

## Returns

Compact count, minimum and maximum change-value observations plus changed partitions and a restricted read predicate.

## Raises / Errors

ValueError
    If table identity, target type, or a required active source-change rule
    is invalid.
RuntimeError
    If ``00_env_config`` has not initialized FabricOps or observation
    cannot be collected or persisted.

## Notes

<div class="reference-docstring-notes" markdown="1">

The stored evidence is the stable ``observation_id`` and ``table_id``, active
``environment_name``, partition value, row count, and earliest and latest change values. This is a lightweight change signal, not proof that
every cell is unchanged: a middle value can change while all three signals
remain identical. Sources without a reliable change column require deeper
change detection elsewhere. Warehouse aggregation is pushed into SQL;
Lakehouse aggregation is distributed and projects only the two required
source columns.
Evidence is appended only after collection succeeds. This function neither
loads history nor makes guardrail decisions; ``check_changes`` owns
comparison and removal tombstones. The stable ``table_id`` is built from the resolved physical identity with the
same logical identity rules used by :func:`profile_and_register_table`. It is
independent of Development or Production; ``environment_name`` keeps those
operational observations separate without requiring a pre-existing catalogue row.

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
