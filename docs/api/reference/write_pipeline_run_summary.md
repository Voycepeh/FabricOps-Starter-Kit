# write_pipeline_run_summary

Write one pipeline runtime summary row to metadata.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:973`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/pipeline.py#L973-L1087">View on GitHub</a>
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
    spark: Any,
    run_id: str,
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
| `spark` | `Any` | Yes | Spark session used to create the one-row summary DataFrame. |
| `run_id` | `str` | Yes | Pipeline run identifier. |
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

    ```text
    write_pipeline_run_summary(...)
    ├── _configured_lakehouse_schema(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   └── _normalize_schema_name(...)
    ├── _definition_name(...)
    ├── _now_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── _get_audit_timezone(...)
    │           └── _validate_audit_timezone(...)
    ├── _summary_status(...)
    ├── resolve_fabric_context(...)
    │   └── get_default_fabric_context(...)
    └── write_lakehouse_table(...)
        ├── _get_store(...)
        │   └── _normalize_path_config(...)
        │       └── PathConfig(...)
        ├── _normalize_table_name(...)
        ├── _resolve_lakehouse_table_path(...)
        │   ├── _normalize_table_name(...)
        │   └── _resolve_lakehouse_schema(...)
        │       └── _normalize_schema_name(...)
        └── resolve_fabric_context(...)
            └── get_default_fabric_context(...)
    ```

??? info "Internal helpers used: 10"

    This callable uses 10 internal helpers for audit timestamp, metadata loading, rule parsing, result summary, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/config.py#L193-L199"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/config.py#L185-L190"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/config.py#L150-L182"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/pipeline.py#L24-L25"><code>_definition_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/config.py#L599-L639"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Result summary</h4>
        <p>Build final statuses, counts, and messages for the caller.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/pipeline.py#L28-L47"><code>_summary_status</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/config.py#L642-L681"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/pipeline.py#L20-L21"><code>_now_iso</code></a>
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
- Source line: `973`
- Inbound references count: 0
- Outbound references count: 6
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
- `fabricops_kit.pipeline._definition_name`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._summary_status`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/pipeline.py#L973-L1087">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f18735b765699aa5069c82d2916cec0a01edd7c8/src/fabricops_kit/pipeline.py#L973-L1087</a>
- Start line: `973`
- End line: `1087`
- Signature:

```python
def write_pipeline_run_summary(
    spark: Any,
    run_id: str,
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

- Internal helper count: 10
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>can_continue</summary>Boolean result that tells downstream notebook code whether processing can keep running.</details>
- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
