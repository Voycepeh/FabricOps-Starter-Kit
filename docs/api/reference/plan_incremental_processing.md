# `plan_incremental_processing`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Select incremental source scope and an explicit target maintenance strategy.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/plan_incremental_processing.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/plan_incremental_processing.py#L10-L115">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def plan_incremental_processing(
    changes_result: dict,
    write_strategy: str,
    partition_column: str | None=None,
    key_columns: list[str] | tuple[str, ...] | None=None,
    effective_column: str | None=None,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> plan = plan_incremental_processing(result, "merge", key_columns=["order_id"])
>>> plan["read_strategy"]
'incremental'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `changes_result` | `dict` | Yes | Structured result returned by :func:`check_changes`. |
| `write_strategy` | `str` | Yes | Target strategy: ``overwrite``, ``append``, ``merge``, or ``scd2``. |
| `partition_column` | `str \| None` | No | Explicit target partition column. It must represent the same identity as the observed source partition column. |
| `key_columns` | `list[str] \| tuple[str, ...] \| None` | No | Business keys required by ``merge`` and ``scd2``. |
| `effective_column` | `str \| None` | No | Incoming sequence/effective column required by ``scd2``. |

## Returns

Plain dictionary describing read scope and target write semantics.

## Raises / Errors

ValueError
    If the evidence or requested strategy is unsafe or incomplete.

## Notes

<div class="reference-docstring-notes" markdown="1">

This function only plans work. It does not read business data or write a
target. Removed partitions are never translated into implicit deletes.

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
