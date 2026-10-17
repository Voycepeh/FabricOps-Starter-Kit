# `check_sensitive_data`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Apply explicit Sensitive Data treatment before a governed write.


## Usage notes

Use after pipeline_write resolves target identity and before the physical governed write.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
sensitive_result = check_sensitive_data(transformed_df, table_id=table_id, raise_on_failure=True)
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def check_sensitive_data(
    dataframe,
    *,
    table_id: str,
    run_id: str='',
    existing_mapping=None,
    enabled: bool=True,
    raise_on_failure: bool=False,
    spark_session=None,
    verbose: bool=True,
) -> dict:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `dataframe` | `pyspark.sql.DataFrame` | Yes | `—` | Prepared business rows whose governed sensitive columns must be treated. |
| `table_id` | `str` | Yes | `—` | Canonical identity used to resolve the applicable exact Data Contract version. |
| `run_id` | `str` | No | `''` | Pipeline run identity recorded with Guardrail summary evidence. |
| `existing_mapping` | `pyspark.sql.DataFrame` | No | `None` | Previously persisted mappings to reuse. Rows are scoped by ``table_id`` and ``column_id``; established original-to-token assignments are preserved. |
| `enabled` | `bool` | No | `True` | Explicitly skip the check and return the supplied DataFrame when ``False``. |
| `raise_on_failure` | `bool` | No | `False` | Raise ``RuntimeError`` when a blocking treatment cannot continue. |
| `spark_session` | `object` | No | `None` | Spark session to use. When omitted, FabricOps uses the supplied DataFrame session or resolves the active session. |
| `verbose` | `bool` | No | `True` | Print the concise normalized check outcome when ``True``. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
result = check_sensitive_data(
    transformed_df,
    table_id=TARGET_TABLE_ID,
    raise_on_failure=True,
)
write_result = pipeline_write(
    result["dataframe"],
    table_id=TARGET_TABLE_ID,
)
```

</div>

## Returns

dict
    ``dataframe`` contains every successfully applied treatment;
    ``support_mapping`` contains caller-owned token mappings, or ``None``;
    ``checks`` contains sanitized outcomes; and ``can_continue`` is false
    only when a Block treatment fails. No mapping is persisted automatically.

## Raises / Errors

RuntimeError
    If ``dataframe`` is not a Spark DataFrame in the Fabric runtime, or
    ``raise_on_failure=True`` and a Block treatment fails. Inspect ``checks``
    and the governed treatment configuration before retrying.

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

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/check_sensitive_data.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/check_sensitive_data.py#L20-L195">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.2.0 |
| Preview | 0.2.5 |


</details>
