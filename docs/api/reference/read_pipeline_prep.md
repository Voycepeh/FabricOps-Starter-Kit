# `read_pipeline_prep`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare governed source observation and read scope without reading business data.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/read_pipeline_prep.py:318`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/read_pipeline_prep.py#L318-L446">View on GitHub</a>
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
def read_pipeline_prep(
    source_table_id: str,
    source_read_strategy: str,
    target_table_id: str | None=None,
    source_watermark_column: str | None=None,
    source_partition_column: str | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> prep = read_pipeline_prep(
...     source_table_id="warehouse:source:dbo:bookings",
...     source_read_strategy="incremental_watermark",
...     target_table_id="lakehouse:unified:dbo:bookings",
...     source_watermark_column="modified_datetime",
... )
>>> prep["read_mode"] in {"skip", "full_dataset", "incremental_subset"}
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `source_table_id` | `str` | Yes | Canonical identity of one registered source table. FabricOps resolves its physical coordinates from the Catalogue. |
| `source_read_strategy` | `str` | Yes | Engineer-authored rule for identifying source data to process. |
| `target_table_id` | `str \| None` | No | Governed target whose ``_watermark_value`` or ``_partition_bucket`` stores successful incremental progress. Required for incremental strategies. |
| `source_watermark_column` | `str \| None` | No | Physical source progress column required by ``incremental_watermark``. |
| `source_partition_column` | `str \| None` | No | Logical bucket column required by ``incremental_partition``. |

## Returns

Registered source identity, target identity for watermark processing, observation and change state, and skip, full, or incremental read scope.

## Raises / Errors

ValueError
    If source identity, configuration, target watermark state, or the resulting
    processing scope is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

Watermark subsets use the bounded interval ``(lower_bound, upper_bound]``.
The first watermark run remains a ``full_dataset`` read, while its scope
retains the watermark column and captured upper bound so write preparation
can verify that target-backed progress reaches the inspected source state.
Successful watermark progress is the maximum target ``_watermark_value``.
Successful partition progress is the set of target ``_partition_bucket``
values. Source Observation remains change-detection evidence and neither
strategy uses a secondary checkpoint commit. Partition change safety resolves
the source table's own processing through :func:`check_changes`; target
selection and publication are intentionally outside this function.

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
