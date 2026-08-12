# `detect_source_changes`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Detect source changes and plan incremental inspection ranges.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/detect_source_changes.py:148`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/detect_source_changes.py#L148-L220">View on GitHub</a>
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
def detect_source_changes(
    current_df: Any,
    previous_df: Any,
    key_columns: Sequence[str],
    incremental_column: str | None=None,
    refresh_days: int=7,
    source_pattern: str='snapshot',
    version_columns: Sequence[str] | None=None,
    comparison_scope: str='complete',
    include_row_changes: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = detect_source_changes(
...     current_df, previous_df, key_columns=["order_id"],
...     incremental_column="order_date", refresh_days=30,
...     source_pattern="mutable_incremental",
... )
>>> result["has_historical_changes"]
False

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `current_df` | `Any` | Yes | Current source state obtained through an existing FabricOps reader. |
| `previous_df` | `Any` | Yes | Previously observed source state with the same columns. |
| `key_columns` | `Sequence[str]` | Yes | Non-null columns defining the logical business key. |
| `incremental_column` | `str \| None` | No | Date or timestamp column used for partition and range planning. |
| `refresh_days` | `int` | No | Positive number of days considered intentionally mutable. |
| `source_pattern` | `str` | No | Explicit source storage pattern, independent of source location or layer. |
| `version_columns` | `Sequence[str] \| None` | No | Version identity columns required for a ``versioned`` source. |
| `comparison_scope` | `str` | No | Comparison completeness. Only ``complete`` permits deletion detection; use ``partial`` for a new-only append read. |
| `include_row_changes` | `bool` | No | Whether to include the Spark DataFrame of classified changed rows. |

## Returns

Structured source ranges, partition facts, row-change counts, flags, and optional row-level changes.

### Return interpretation

Treat the result as observed facts, not as an instruction to write, warn, or stop.

## Raises / Errors

ValueError for invalid patterns, scopes, windows, columns, null keys, or ambiguous keys.

### Common failure causes

- The comparison scope does not describe the supplied DataFrames.
- Configured logical keys are null or non-unique.
- The incremental column cannot be interpreted as a date for the recent window.

## Notes

<div class="reference-docstring-notes" markdown="1">

This function runs Spark actions in a Fabric-compatible PySpark runtime.
Absence is a deletion only when ``comparison_scope="complete"``.

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
