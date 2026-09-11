# `check_source_stability`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Detect mutation of previously processed source data and validate compatibility with the governed target load strategy.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_source_stability.py:347`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_source_stability.py#L347-L392">View on GitHub</a>
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
def check_source_stability(observation, *, target_table_id: str) -> dict
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> observation = observe_table("orders", target="source", schema="dbo")
>>> result = check_source_stability(observation, target_table_id="lakehouse:unified:dbo:orders")
>>> result["load_strategy"]
'append'

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `observation` | `pyspark.sql.DataFrame` | Yes | Canonical evidence returned by :func:`observe_table`. |
| `target_table_id` | `str` | Yes | Governed target identity whose frozen Data Contract supplies the authoritative load strategy. |

## Returns

First-observation, changed or unchanged, and new, changed, removed, or reappeared partition evidence.

## Raises / Errors

ValueError
    If the observation, Source Stability rule, or target processing is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

The comparison baseline is the observation referenced by the latest
``METADATA_SOURCE_CONSUMPTION`` record for the active logical notebook
name, source ``table_id``, and ``target_table_id``. Raw observations from
failed attempts or other source-to-target relationships are not baselines.

New source data is compatible with append. Mutation, removal, or
reappearance of previously processed data violates append stability;
overwrite, SCD1, and SCD2 report that evidence as compatible because their
governed write semantics can reconcile it. This Guardrail detects and
validates evidence; it does not execute the load strategy.

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
