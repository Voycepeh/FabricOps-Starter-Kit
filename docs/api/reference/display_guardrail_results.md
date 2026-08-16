# `display_guardrail_results`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Prepare in-memory or persisted guardrail evidence for Fabric notebook review.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/display_guardrail_results.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/display_guardrail_results.py#L10-L29">View on GitHub</a>
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
def display_guardrail_results(
    result_bundle: Mapping[str, Any] | None=None,
    mode: str='summary',
    spark_session: Any | None=None,
    metadata_table_key: str | None=None,
    run_id: str | None=None,
    target: str='metadata',
    schema: str | None=None,
) -> Any:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
guardrail_views = display_guardrail_results(metadata_table_key=selected_metadata_table_key, target="metadata", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `result_bundle` | `Mapping[str, Any] \| None` | No | Optional in-memory guardrail result bundle. |
| `mode` | `str` | No | In-memory display mode: summary, detailed, or debug. |
| `spark_session` | `Any \| None` | No | Spark session used for persisted evidence or optional in-memory DataFrames. |
| `metadata_table_key` | `str \| None` | No | Canonical table identity used to scope persisted Guardrail Results. |
| `run_id` | `str \| None` | No | Optional exact execution; otherwise the latest canonical-table run is selected. |
| `target` | `str` | No | Configured metadata FabricStore target. |
| `schema` | `str \| None` | No | Optional metadata lakehouse schema override. |

## Returns

In-memory display rows, or persisted summary and row-evidence Spark DataFrames for one selected run.

### Return interpretation

Persisted mode returns summary and row_evidence Spark DataFrames for one run; in-memory modes retain their existing display formats.

## Raises / Errors

Raises ValueError for conflicting inputs, missing persisted-mode inputs, or unsupported in-memory mode.

### Common failure causes

- Mode is not summary, detailed, or debug.
- The Spark session cannot create a DataFrame from display rows.
- The result bundle is malformed.
- The caller expects debug internals while using summary mode.

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

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |
| Preview | 0.2.0 |


</details>
