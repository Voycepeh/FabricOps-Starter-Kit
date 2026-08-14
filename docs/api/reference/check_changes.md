# `check_changes`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Describe deterministic partition and logical-row source changes.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_changes.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_changes.py#L8-L91">View on GitHub</a>
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
def check_changes(
    dataframe,
    previous_dataframe=None,
    partition_columns: list[str] | tuple[str, ...] | None=None,
    key_columns: list[str] | tuple[str, ...] | None=None,
    non_key_columns: list[str] | tuple[str, ...] | None=None,
    range_column: str | None=None,
    source_pattern: str='snapshot',
    comparison_scope: str='complete',
    refresh_days: int=0,
    version_column: str | None=None,
    reference_date: date | datetime | str | None=None,
    include_row_changes: bool=False,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_changes(current, previous, key_columns=["id"])
>>> result["changed"]
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `DataFrame or iterable of mappings` | Yes | Current source observation. |
| `previous_dataframe` | `DataFrame or iterable of mappings` | No | Previous comparable source observation. |
| `partition_columns` | `list[str] \| tuple[str, ...] \| None` | No | Columns defining cheap partition fingerprints. |
| `key_columns` | `list[str] \| tuple[str, ...] \| None` | No | Non-null columns that uniquely identify a logical row. |
| `non_key_columns` | `list[str] \| tuple[str, ...] \| None` | No | Columns whose content identifies an update. Defaults to all non-key columns, except that a versioned source's ``version_column`` is used only for latest-record resolution unless explicitly included here. |
| `range_column` | `str \| None` | No | Date, timestamp, or ordered range column used for recent and unseen range classification. |
| `source_pattern` | `str` | No | Explicit source behavior; it is never inferred from table naming. |
| `comparison_scope` | `str` | No | Completeness of the current observation. ``complete`` can prove global deletions, ``partitions`` can prove deletions only inside supplied complete partitions, and ``partial`` never infers deletions. |
| `refresh_days` | `int` | No | Number of days in the expected mutable window. Zero means only values dated on ``reference_date`` are recent. |
| `version_column` | `str \| None` | No | Column used to select the latest row per logical key. Required when ``source_pattern="versioned"``. |
| `reference_date` | `date \| datetime \| str \| None` | No | End of the recent mutable window. |
| `include_row_changes` | `bool` | No | Include deterministic key hashes grouped by change classification. |

## Returns

Structured change counts, partition fingerprints, recent and historical classifications, and observed ranges.

## Raises / Errors

ValueError
    If configuration is invalid or logical keys are null, missing, or
    duplicated.

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
