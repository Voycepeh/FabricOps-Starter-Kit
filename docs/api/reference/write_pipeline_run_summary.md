# write_pipeline_run_summary

Write one pipeline runtime summary row to metadata.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:1152`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321">View on GitHub</a>
</div>

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

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- `fabricops_kit.fabric_input_output.write_lakehouse_table`
- `fabricops_kit.pipeline._active_pipeline_context`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._summary_status`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`

**Side effects:**

Writes METADATA_PIPELINE_RUNS through the configured metadata lakehouse target.

**Notes:**

The row is written via ``write_lakehouse_table(..., metadata_table,
target="metadata", context=resolved_context, mode="append")`` so runtime
evidence never relies on a default attached lakehouse.

</details>

??? info "Call flow"

    Unique internal helpers: 14. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>write_pipeline_run_summary(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L154-L156"><code>_active_pipeline_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L163-L164"><code>_definition_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L167-L186"><code>_summary_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
    </div>

    ### Refactor signals

    These generated hints point maintainers to call-tree shapes worth reviewing; they are not automatic refactor requirements.

    **Helpers appearing in multiple branches**

    - `_get_store` appears in 2 branches.
    - `_normalize_path_config` appears in 2 branches.
    - `_normalize_schema_name` appears in 2 branches.
    - `_normalize_table_name` appears in 2 branches.

    **Call chains deeper than 4 levels**

    - None detected.

    **Helpers that only call one package-local helper**

    - `_current_audit_timestamp` only delegates to `_get_audit_timezone`.
    - `_get_audit_timezone` only delegates to `_validate_audit_timezone`.
    - `_get_store` only delegates to `_normalize_path_config`.
    - `_resolve_lakehouse_schema` only delegates to `_normalize_schema_name`.
    - `_now_iso` only delegates to `_current_audit_timestamp`.

    **Helpers grouped into possibly wrong areas**

    - None detected from helper names, doc summaries, and module placement.

This callable uses 14 internal helpers for audit timestamp, metadata loading, rule parsing, result summary, fabric or spark access, and other.

<div class="reference-helper-groups">
  <section class="reference-helper-group">
    <h4>Audit timestamp</h4>
    <p>Resolve and stamp audit time consistently.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Metadata loading</h4>
    <p>Load and identify the metadata or table context needed by the callable.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Rule parsing</h4>
    <p>Normalize stored or user-provided values before applying rules.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L163-L164"><code>_definition_name</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Result summary</h4>
    <p>Build final statuses, counts, and messages for the caller.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L167-L186"><code>_summary_status</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Fabric or Spark access</h4>
    <p>Access Fabric or Spark runtime services used by the implementation.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Other</h4>
    <p>Support lower-level implementation details that do not fit the main helper areas.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L154-L156"><code>_active_pipeline_context</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L160"><code>_now_iso</code></a>
    </div>
  </section>
</div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_pipeline_run_summary`
- Short name: `write_pipeline_run_summary`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `1152`
- Inbound references count: 0
- Outbound references count: 7
- Used in templates: 02_pipeline
- Glossary terms: guardrails, can_continue, evidence, metadata lakehouse

### Implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Runtime summary`.
- **inputs:** spark, config, env, run_id, agreement context, source/target definitions, guardrail results, and evidence statuses.
- **output:** Runtime summary row that was written.
- **side_effects:** Writes METADATA_PIPELINE_RUNS through the configured metadata lakehouse target.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- `fabricops_kit.fabric_input_output.write_lakehouse_table`
- `fabricops_kit.pipeline._active_pipeline_context`
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._summary_status`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1152-L1321</a>
- Start line: `1152`
- End line: `1321`
- Signature:

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

### Internal relationship graph

### Public related functions

- `fabricops_kit.pipeline.write_catalogue_evidence`
- <a href="write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="write_data/"><code>fabricops_kit.fabric_input_output.write_data</code></a>

### Internal implementation summary

- Internal helper count: 14
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<details class="glossary-chip"><summary>Guardrails</summary><span>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></details>
<details class="glossary-chip"><summary>can_continue</summary><span>Boolean result that tells downstream notebook code whether processing can keep running.</span> <a href="../../../reference/glossary/#cancontinue">Full definition</a></details>
<details class="glossary-chip"><summary>Evidence</summary><span>Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></details>
<details class="glossary-chip"><summary>Metadata lakehouse</summary><span>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></details>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
