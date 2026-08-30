# `read_pipeline_prep`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare governed source observation and read scope without reading business data.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/read_pipeline_prep.py:269`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/read_pipeline_prep.py#L269-L410">View on GitHub</a>
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
    source_table_name: str,
    target_table_name: str,
    source_read_strategy: str,
    source_watermark_column: str | None=None,
    source_partition_column: str | None=None,
    source_target: str='source',
    source_schema: str | None=None,
    target: str='unified',
    schema: str | None=None,
    load_strategy: str,
    load_strategy_parameters: dict[str, Any] | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> prep = read_pipeline_prep(
...     "bookings", "bookings_curated", source_schema="dbo", schema="dbo",
...     source_read_strategy="incremental_watermark",
...     source_watermark_column="modified_datetime", load_strategy="scd1",
...     load_strategy_parameters={"key_columns": ["booking_id"]},
... )
>>> prep["read_mode"] in {"skip", "full_dataset", "incremental_subset"}
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `source_table_name` | `str` | Yes | Physical source table to prepare. |
| `target_table_name` | `str` | Yes | Governed target table whose target processing definition controls this run. |
| `source_read_strategy` | `str` | Yes | Engineer-authored rule for identifying source data to process. |
| `source_watermark_column` | `str \| None` | No | Checkpoint column required by ``incremental_watermark``. |
| `source_partition_column` | `str \| None` | No | Logical bucket column required by ``incremental_partition``. |
| `source_target` | `str` | No | Configured source Lakehouse or Warehouse target. |
| `source_schema` | `str \| None` | No | Optional source schema. |
| `target` | `str` | No | Configured governed target. |
| `schema` | `str \| None` | No | Optional governed target schema. |
| `load_strategy` | `str` | Yes | Independent target application strategy. |
| `load_strategy_parameters` | `dict[str, Any] \| None` | No | Parameters owned by the target strategy. |

## Returns

Observation and change evidence, canonical processing, and skip, full, or incremental read scope.

## Raises / Errors

ValueError
    If source configuration, checkpoint state, contract processing, or the
    resulting processing scope is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

Watermark subsets use the bounded interval ``(lower_bound, upper_bound]``.
The successful checkpoint remains unchanged until a later post-write commit
succeeds. Partition subsets reuse FabricOps source observation and change
detection; full-dataset reads do not observe the source merely to skip it.

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
