# `write_pipeline_run_summary`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 51
- Shared helpers: 25
- Private helpers: 26

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=write_pipeline_run_summary">Open Preview call flow</a>

Write one pipeline runtime summary row to metadata.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/write_pipeline_run_summary.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/write_pipeline_run_summary.py#L10-L69">View on GitHub</a>
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
def write_pipeline_run_summary(
    spark: Any | None=None,
    context: dict[str, Any] | None=None,
    agreement_id: str='',
    agreement_version: str='',
    notebook_type: str='02_pipeline',
    started_at: str | None=None,
    completed_at: str | None=None,
    status: str='completed',
    source_definitions: Mapping[str, Mapping[str, Any]] | None=None,
    target_definitions: Mapping[str, Mapping[str, Any]] | None=None,
    source_schema_results: Mapping[str, Mapping[str, Any]] | None=None,
    target_schema_results: Mapping[str, Mapping[str, Any]] | None=None,
    source_freshness_results: Mapping[str, Mapping[str, Any]] | None=None,
    target_freshness_results: Mapping[str, Mapping[str, Any]] | None=None,
    source_stability_results: Mapping[str, Mapping[str, Any]] | None=None,
    target_stability_results: Mapping[str, Mapping[str, Any]] | None=None,
    source_dq_results: Mapping[str, Mapping[str, Any]] | None=None,
    target_dq_results: Mapping[str, Mapping[str, Any]] | None=None,
    lineage_status: str='not_run',
    catalogue_status: str='not_run',
    message: str='',
    source_guardrail_results: Mapping[str, Any] | None=None,
    target_guardrail_results: Mapping[str, Any] | None=None,
    target_write_status: Mapping[str, Any] | None=None,
    lineage_result: Mapping[str, Any] | None=None,
    metadata_table: str=METADATA_PIPELINE_RUNS_TABLE,
    mode: str='append',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any \| None` | No | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |
| `agreement_id` | `str` | No | Not documented yet |
| `agreement_version` | `str` | No | Not documented yet |
| `notebook_type` | `str` | No | Not documented yet |
| `started_at` | `str \| None` | No | Not documented yet |
| `completed_at` | `str \| None` | No | Not documented yet |
| `status` | `str` | No | Not documented yet |
| `source_definitions` | `list[PipelineTableConfig]` | No | Not documented yet |
| `target_definitions` | `list[PipelineTableConfig]` | No | Not documented yet |
| `source_schema_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_schema_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_freshness_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_freshness_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_stability_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_stability_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_dq_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_dq_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `lineage_status` | `str` | No | Not documented yet |
| `catalogue_status` | `str` | No | Not documented yet |
| `message` | `str` | No | Not documented yet |
| `source_guardrail_results` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `target_guardrail_results` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `target_write_status` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `lineage_result` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `metadata_table` | `str` | No | Not documented yet |
| `mode` | `str` | No | Not documented yet |

## Returns

Runtime summary row that was written.

### Return interpretation

The returned summary shows what run metadata was assembled or written. Compare status and guardrail counts with expected pipeline outcomes.

## Raises / Errors

Not documented yet

### Common failure causes

- Required run identifiers are missing.
- Guardrail result structures are malformed.
- Metadata routing is unavailable.
- The configured summary table cannot be written.

## See also

- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)
- [Metadata Tables](../../reference/metadata.md)


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

!!! info "Generated reference freshness"
    Reference pages generated: 10 Jul 2026, 2:29 AM SGT
    Call-flow data generated: 10 Jul 2026, 2:29 AM SGT
