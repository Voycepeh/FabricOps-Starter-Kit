# start_pipeline_run

Start a guided pipeline run and store active runtime context.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:86`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L86-L124">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in advanced guided pipelines that do not need agreement selection.

### Do not use when

- Use lower-level explicit APIs directly when an advanced custom notebook must pass runtime context manually.

### Additional context

Start a guided pipeline run and store active runtime context.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def start_pipeline_run(
    run_context: Any=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    pipeline_name: str | None=None,
    context: dict[str, Any] | None=None,
) -> PipelineRunContext:
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
| `run_context` | `Any` | No | ``RUN_CONTEXT`` from ``00_env_config``. Defaults to the active notebook variable named ``RUN_CONTEXT``. |
| `spark_session` | `Any` | No | Spark session. Defaults to the active notebook variable named ``spark``. |
| `metadata_schema` | `str \| None` | No | ``METADATA_SCHEMA`` from ``00_env_config`` when schema routing is used. |
| `pipeline_name` | `str \| None` | No | Friendly pipeline name. Defaults to Fabric runtime notebook metadata. |
| `context` | `dict[str, Any] \| None` | No | Advanced FabricOps context override. |

## Returns

Active PipelineRunContext.

### Return interpretation

Active PipelineRunContext.

## Raises / Errors

Not documented yet

### Common failure causes

- No active pipeline context exists.
- Fabric runtime variables are unavailable.
- Configured metadata routing is unavailable.

## Relationships

### Used by

- <a href="start_pipeline_run_with_agreement/"><code>fabricops_kit.pipeline.start_pipeline_run_with_agreement</code></a>

### Calls

- <a href="PipelineRunContext/"><code>fabricops_kit.pipeline.PipelineRunContext</code></a>
- `fabricops_kit.pipeline._notebook_global`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_metadata_value`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

None.

**Side effects:**

May read or store active notebook runtime context for downstream guided wrappers.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    start_pipeline_run(...)
    ├── _notebook_global(...)
    ├── _now_iso(...)
    │   └── _current_audit_timestamp(...)
    │       └── _get_audit_timezone(...)
    │           └── _validate_audit_timezone(...)
    ├── _runtime_metadata_value(...)
    └── PipelineRunContext(...)
    ```

??? info "Internal helpers used: 6"

    This callable uses 6 internal helpers for audit timestamp, metadata loading, rule parsing, and other.

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
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L79-L83"><code>_runtime_metadata_value</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L70-L76"><code>_notebook_global</code></a>
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

- Fully qualified function name: `fabricops_kit.pipeline.start_pipeline_run`
- Short name: `start_pipeline_run`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `86`
- Inbound references count: 1
- Outbound references count: 4
- Used in templates: —
- Glossary terms: notebook template, guardrails, metadata lakehouse

### Implementation contract

- **required_context:** Defaults to RUN_CONTEXT, spark, and METADATA_SCHEMA from 00_env_config when available.
- **inputs:** See the source docstring for optional advanced overrides.
- **output:** Active PipelineRunContext.
- **side_effects:** May read or store active notebook runtime context for downstream guided wrappers.
- **failure_modes:** Not documented yet
- **verification:** Verify guided notebooks call start_pipeline_run_with_agreement before profile or enforcement wrappers.

### Inbound references

- <a href="start_pipeline_run_with_agreement/"><code>fabricops_kit.pipeline.start_pipeline_run_with_agreement</code></a>

### Outbound references

- <a href="PipelineRunContext/"><code>fabricops_kit.pipeline.PipelineRunContext</code></a>
- `fabricops_kit.pipeline._notebook_global`
- `fabricops_kit.pipeline._now_iso`
- `fabricops_kit.pipeline._runtime_metadata_value`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L86-L124">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L86-L124</a>
- Start line: `86`
- End line: `124`
- Signature:

```python
def start_pipeline_run(
    run_context: Any=None,
    spark_session: Any=None,
    metadata_schema: str | None=None,
    pipeline_name: str | None=None,
    context: dict[str, Any] | None=None,
) -> PipelineRunContext:
```

### Internal relationship graph

### Public related functions

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Internal implementation summary

- Internal helper count: 6
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>
- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
