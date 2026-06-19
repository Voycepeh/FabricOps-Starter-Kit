# complete_pipeline_run

Write the guided pipeline run summary from active context and results.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:1030`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1030-L1079">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use at the end of guided 02_pipeline after enforcement, writes, and lineage.

### Do not use when

- Use lower-level explicit APIs directly when an advanced custom notebook must pass runtime context manually.

### Additional context

Write the guided pipeline run summary from active context and results.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def complete_pipeline_run(
    source_guardrail_results: Mapping[str, Any],
    target_guardrail_results: Mapping[str, Any],
    target_write_status: Mapping[str, Any] | None=None,
    lineage_result: Mapping[str, Any] | None=None,
    message: str='',
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
PIPELINE = start_pipeline_run_with_agreement()
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `source_guardrail_results` | `Mapping[str, Any]` | Yes | Enforcement result bundles returned by :func:`enforce_source_guardrails` and :func:`enforce_target_guardrails`. |
| `target_guardrail_results` | `Mapping[str, Any]` | Yes | Not documented yet |
| `target_write_status` | `Mapping[str, Any] \| None` | No | Target write outcome mapping created by the notebook write step. |
| `lineage_result` | `Mapping[str, Any] \| None` | No | Lineage write result returned by :func:`write_pipeline_lineage`. |
| `message` | `str` | No | Additional runtime summary message. |

## Returns

Summary row returned by write_pipeline_run_summary.

### Return interpretation

Summary row returned by write_pipeline_run_summary.

## Raises / Errors

Not documented yet

### Common failure causes

- No active pipeline context exists.
- Fabric runtime variables are unavailable.
- Configured metadata routing is unavailable.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.pipeline._pipeline_status_from_results`
- <a href="get_active_pipeline_context/"><code>fabricops_kit.pipeline.get_active_pipeline_context</code></a>
- <a href="write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`

**Side effects:**

May read or store active notebook runtime context for downstream guided wrappers.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    complete_pipeline_run(...)
    ├── _pipeline_status_from_results(...)
    ├── get_active_pipeline_context(...)
    └── write_pipeline_run_summary(...)
        ├── _configured_lakehouse_schema(...)
        │   └── …
        ├── _definition_name(...)
        ├── _now_iso(...)
        │   └── …
        ├── _summary_status(...)
        ├── resolve_fabric_context(...)
        │   └── …
        └── write_lakehouse_table(...)
            └── …
    ```

??? info "Internal helpers used: 14"

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
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L183-L184"><code>_definition_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Result summary</h4>
        <p>Build final statuses, counts, and messages for the caller.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1026-L1027"><code>_pipeline_status_from_results</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L187-L206"><code>_summary_status</code></a>
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
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L179-L180"><code>_now_iso</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.complete_pipeline_run`
- Short name: `complete_pipeline_run`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `1030`
- Inbound references count: 0
- Outbound references count: 3
- Used in templates: 02_pipeline
- Glossary terms: notebook template, guardrails, metadata lakehouse

### Implementation contract

- **required_context:** Defaults to RUN_CONTEXT, spark, and METADATA_SCHEMA from 00_env_config when available.
- **inputs:** See the source docstring for optional advanced overrides.
- **output:** Summary row returned by write_pipeline_run_summary.
- **side_effects:** May read or store active notebook runtime context for downstream guided wrappers.
- **failure_modes:** Not documented yet
- **verification:** Verify guided notebooks call start_pipeline_run_with_agreement before profile or enforcement wrappers.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.pipeline._pipeline_status_from_results`
- <a href="get_active_pipeline_context/"><code>fabricops_kit.pipeline.get_active_pipeline_context</code></a>
- <a href="write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1030-L1079">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L1030-L1079</a>
- Start line: `1030`
- End line: `1079`
- Signature:

```python
def complete_pipeline_run(
    source_guardrail_results: Mapping[str, Any],
    target_guardrail_results: Mapping[str, Any],
    target_write_status: Mapping[str, Any] | None=None,
    lineage_result: Mapping[str, Any] | None=None,
    message: str='',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Internal implementation summary

- Internal helper count: 14
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>
- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
