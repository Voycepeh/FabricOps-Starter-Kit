# `check_and_profile_source`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Apply governed source DQ and canonical-or-diagnostic profiling.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_and_profile_source.py:18`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_and_profile_source.py#L18-L123">View on GitHub</a>
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
def check_and_profile_source(
    dataframe,
    source_prep: Mapping[str, Any],
    register_full_profile: bool=True,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_and_profile_source(source_df, source_prep=source_prep)
>>> result["profile_kind"] in {"canonical", "diagnostic"}
True

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `pyspark.sql.DataFrame` | Yes | Physical source rows read with the ``scope`` returned by :func:`read_pipeline_prep`. |
| `source_prep` | `Mapping[str, Any]` | Yes | Governed preparation returned by :func:`read_pipeline_prep` for the same source. |
| `register_full_profile` | `bool` | No | Register a canonical profile when preparation selected the complete physical source. Set this to ``False`` when ``dataframe`` is an engineer-authored query result rather than the registered source table itself. |

## Returns

Governed DQ result, profile DataFrame, and canonical or diagnostic profile kind.

## Raises / Errors

ValueError
    If ``source_prep`` is malformed, represents a skipped read, or
    ``register_full_profile`` is not Boolean.
RuntimeError
    If a blocking DQ Guardrail rejects the source or metadata persistence
    required for a canonical profile is unavailable.

## Notes

<div class="reference-docstring-notes" markdown="1">

A ``full_dataset`` read may replace the current canonical source profile.
An ``incremental_subset`` is always diagnostic and never writes
``METADATA_DATA_PROFILED``, ``METADATA_DATA_PROFILED_FREQUENCY``, or
``METADATA_DATA_CATALOGUE``. Governed DQ results continue to be written to
``METADATA_GUARDRAIL_RESULTS``.

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
