# `write_pipeline_lineage`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 46
- Shared helpers: 22
- Private helpers: 24

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=write_pipeline_lineage">Open Preview call flow</a>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview |
| Live-critical dependencies | 0 |
| Direct Live dependents | 0 |
| Transitive Live dependents | 0 |


Write many-to-many source-to-target lineage evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/write_pipeline_lineage.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/write_pipeline_lineage.py#L10-L35">View on GitHub</a>
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
def write_pipeline_lineage(
    spark: Any,
    context: dict[str, Any] | None=None,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None=None,
    dataset_name: str='',
    agreement_id: str='',
    agreement_version: str='',
    metadata_table: str=LINEAGE_TABLE,
    mode: str='append',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |
| `source_definitions` | `list[PipelineTableConfig]` | Yes | Not documented yet |
| `target_definitions` | `list[PipelineTableConfig]` | Yes | Not documented yet |
| `relationships` | `list[Mapping[str, Any]] \| None` | No | Not documented yet |
| `dataset_name` | `str` | No | Not documented yet |
| `agreement_id` | `str` | No | Not documented yet |
| `agreement_version` | `str` | No | Not documented yet |
| `metadata_table` | `str` | No | Not documented yet |
| `mode` | `str` | No | Not documented yet |

## Returns

Status, row count, and lineage rows.

### Return interpretation

A successful result indicates lineage rows were prepared for metadata persistence; review returned counts against expected transformation steps.

## Raises / Errors

Not documented yet

### Common failure causes

- Lineage records are empty or malformed.
- run_id, source, or target identifiers are missing.
- The metadata table cannot be written.
- Audit fields cannot be resolved from configuration.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Metadata Tables](../../reference/metadata.md)


!!! info "Generated reference freshness"
    Reference pages generated: 08 Jul 2026, 1:08 PM SGT
    Call-flow data generated: 09 Jul 2026, 8:52 PM SGT
