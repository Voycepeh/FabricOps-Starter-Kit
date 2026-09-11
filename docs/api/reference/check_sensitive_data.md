# `check_sensitive_data`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Apply explicit Sensitive Data treatment before a governed write.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_sensitive_data.py:150`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_sensitive_data.py#L150-L311">View on GitHub</a>
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
def check_sensitive_data(
    dataframe,
    table_id: str,
    run_id: str='',
    existing_mapping=None,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> result = check_sensitive_data(transformed_df, table_id=TARGET_TABLE_ID)
>>> stop_if_failed(result)
>>> write_prep = write_pipeline_prep(result["dataframe"], target_table_id=TARGET_TABLE_ID, source_preps=sources)

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `pyspark.sql.DataFrame` | Yes | Prepared business rows whose governed sensitive columns must be treated. |
| `table_id` | `str` | Yes | Canonical identity used to resolve the applicable exact Data Contract version. |
| `run_id` | `str` | No | Pipeline run identity recorded with Guardrail summary evidence. |
| `existing_mapping` | `pyspark.sql.DataFrame` | No | Previously persisted mappings to reuse. Rows are scoped by ``table_id`` and ``column_id``; established original-to-token assignments are preserved. |

## Returns

Treated DataFrame, optional caller-owned token mapping, sanitized checks, and continuation decision.

## Raises / Errors

RuntimeError
    If ``dataframe`` is not a Spark DataFrame in the Fabric runtime.

## Notes

<div class="reference-docstring-notes" markdown="1">

Only active ``sensitive_data`` Guardrails from the exact applicable Data
Contract version are processed. Classification Enrichment is never read and
never triggers a transformation. ``tokenize`` creates opaque UUID tokens
that are consistent within the returned mapping/run and preserves nulls;
supplying ``existing_mapping`` preserves established assignments. Cross-run
stability otherwise requires the project to persist and supply the mapping.
``mask`` preserves configured leading and trailing characters and replaces
each hidden character. ``bucket`` replaces numeric values with row-preserving
labels: values below the first bin use the first label, each later bin is an
inclusive lower boundary, and values at or above the final bin use the final
label. Bucket does not aggregate rows. ``remove`` drops the governed column.
Warn failures leave the input unchanged
for that rule and permit continuation, while Block failures require callers
to stop before writing. Raw values exist only in the returned support mapping
and are excluded from ``METADATA_GUARDRAIL_RESULTS``.

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
