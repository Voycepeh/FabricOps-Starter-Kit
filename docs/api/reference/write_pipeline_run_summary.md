# write_pipeline_run_summary

??? info "Downstream callables: 39"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>write_pipeline_run_summary(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1340-L1531"><code>_write_pipeline_run_summary_workflow(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L239-L247"><code>configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L49-L60"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L263-L287"><code>write_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L192-L197"><code>normalize_write_mode(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L146-L150"><code>resolve_configured_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L166-L170"><code>resolve_lakehouse_table_location(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L37-L46"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L85-L87"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L90-L93"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29"><code>_join_lakehouse_area_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136"><code>resolve_target_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72"><code>_validate_warehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L200-L203"><code>validate_dataframe_writer(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L229-L236"><code>write_delta_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L98-L112"><code>coerce_metadata_row_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L105-L120"><code>_metadata_table_schema_registry(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L100-L102"><code>_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L85-L97"><code>_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_metadata_tables.py#L34-L82"><code>_spark_types(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L70-L95"><code>_coerce_metadata_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L234-L236"><code>_active_pipeline_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L252-L253"><code>_definition_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L278-L289"><code>_runtime_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L239-L312"><code>_build_runtime_audit_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L164-L172"><code>get_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L156-L161"><code>get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L116-L148"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L193-L205"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L212-L236"><code>_runtime_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L208-L209"><code>_safe_str(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L256-L275"><code>_summary_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L243-L249"><code>_timestamp_value(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L65-L67"><code>_audit_timestamp_value(...)</code></a></div>
    </div>

Write one pipeline runtime summary row to metadata.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:1632`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1632-L1681">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
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
| `spark` | `Any \| None` | No | Not documented yet |
| `run_id` | `str \| None` | No | Not documented yet |
| `context` | `dict[str, Any] \| None` | No | Not documented yet |
| `agreement_id` | `str` | No | Not documented yet |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `notebook_type` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `started_at` | `str \| None` | No | Not documented yet |
| `completed_at` | `str \| None` | No | Not documented yet |
| `status` | `str` | No | Not documented yet |
| `source_definitions` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
| `target_definitions` | `Mapping[str, Mapping[str, Any]] \| None` | No | Not documented yet |
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
