# write_pipeline_run_summary

??? info "Uses 16 internal helper functions"

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>write_pipeline_run_summary(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L158-L160"><code>_active_pipeline_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L165-L173"><code>_configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L682-L721"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L639-L679"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L227-L248"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L85-L96"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L167-L168"><code>_definition_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L163-L164"><code>_now_iso(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L215"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L171-L190"><code>_summary_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="../write_lakehouse_table/"><code>write_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L186-L206"><code>_write_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L682-L721"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L639-L679"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L227-L248"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L85-L96"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L73-L82"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L99-L104"><code>_normalize_write_mode(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L107-L110"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L121-L124"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
    </div>

Write one pipeline runtime summary row to metadata.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>pipeline</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage guidance

### Use when

- Use at the end of 02_pipeline when downstream operators need one metadata record describing the run outcome.

### Additional context

Writes a compact run-level summary that ties pipeline name, agreement context, guardrail results, lineage, and write outcomes together.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_pipeline_run_summary(
    spark: Any | None=None,
    run_id: str | None=None,
    context: dict[str, Any] | None=None,
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    notebook_type: str='02_pipeline',
    pipeline_name: str='',
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
| `spark` | `Any \| None` | No | Spark session used to create the one-row summary DataFrame. When omitted, the active context from :func:`start_pipeline_run` is used. |
| `run_id` | `str \| None` | No | Pipeline run identifier. When omitted, the active context from :func:`start_pipeline_run` is used. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `agreement_id` | `str` | No | Agreement and notebook registry context. |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `notebook_type` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `started_at` | `str \| None` | No | Runtime timestamps. Defaults to current UTC time when omitted. |
| `completed_at` | `str \| None` | No | Not documented yet |
| `status` | `str` | No | Overall pipeline status. |
| `source_definitions` | `Mapping[str, Mapping[str, Any]] \| None` | No | Dataset definitions used to compute source and target counts. |
| `target_definitions` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_schema_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Guardrail result dictionaries included in the JSON summary. |
| `target_schema_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_freshness_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_freshness_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_stability_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_stability_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `source_dq_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_dq_results` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `lineage_status` | `str` | No | Evidence write statuses and support message. |
| `catalogue_status` | `str` | No | Not documented yet |
| `message` | `str` | No | Not documented yet |
| `source_guardrail_results` | `Mapping[str, Any] \| None` | No | Template-facing guardrail result bundles returned by :func:`run_table_guardrails`. When supplied, schema, freshness, profile behavior, DQ, catalogue, and status fields are derived automatically. |
| `target_guardrail_results` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `target_write_status` | `Mapping[str, Any] \| None` | No | Template-facing write and lineage outcomes included in the run summary. |
| `lineage_result` | `Mapping[str, Any] \| None` | No | Not documented yet |
| `metadata_table` | `str` | No | Metadata table that stores runtime summaries. |
| `mode` | `str` | No | Write mode for the runtime summary row. |

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

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">can_continue</span><span class="glossary-chip-definition">Boolean result that tells downstream notebook code whether processing can keep running.</span> <a href="../../../reference/glossary/#cancontinue">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Evidence</span><span class="glossary-chip-definition">Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)
- [Metadata Tables](../../reference/metadata.md)
