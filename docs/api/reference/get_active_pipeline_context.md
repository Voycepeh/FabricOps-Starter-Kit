# get_active_pipeline_context

Return the active guided pipeline context.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:159`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L176">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use inside guided wrappers or custom notebook cells that need resolved runtime context.

### Do not use when

- Use lower-level explicit APIs directly when an advanced custom notebook must pass runtime context manually.

### Additional context

Return the active guided pipeline context.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def get_active_pipeline_context() -> PipelineRunContext
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
PIPELINE = start_pipeline_run_with_agreement()
```

</div>

## Parameters

No parameters.

## Returns

Active PipelineRunContext.

### Return interpretation

Active PipelineRunContext.

## Raises / Errors

RuntimeError
    If no guided pipeline context has been started.

### Common failure causes

- No active pipeline context exists.
- Fabric runtime variables are unavailable.
- Configured metadata routing is unavailable.

## Relationships

### Used by

- `fabricops_kit.pipeline._run_active_table_guardrails`
- <a href="complete_pipeline_run/"><code>fabricops_kit.pipeline.complete_pipeline_run</code></a>

### Calls

Not documented yet

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
    get_active_pipeline_context(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `get_active_pipeline_context` does not have package-local helper descendants in the generated call graph.

    <div class="reference-helper-groups">
      <section class="reference-helper-group reference-helper-group-empty">
        <h4>No internal helpers detected</h4>
        <p>This callable does not have package-local helper descendants in the generated call graph.</p>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.get_active_pipeline_context`
- Short name: `get_active_pipeline_context`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `159`
- Inbound references count: 2
- Outbound references count: 0
- Used in templates: —
- Glossary terms: notebook template, guardrails, metadata lakehouse

### Implementation contract

- **required_context:** Defaults to RUN_CONTEXT, spark, and METADATA_SCHEMA from 00_env_config when available.
- **inputs:** See the source docstring for optional advanced overrides.
- **output:** Active PipelineRunContext.
- **side_effects:** May read or store active notebook runtime context for downstream guided wrappers.
- **failure_modes:** RuntimeError
    If no guided pipeline context has been started.
- **verification:** Verify guided notebooks call start_pipeline_run_with_agreement before profile or enforcement wrappers.

### Inbound references

- `fabricops_kit.pipeline._run_active_table_guardrails`
- <a href="complete_pipeline_run/"><code>fabricops_kit.pipeline.complete_pipeline_run</code></a>

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L176">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L159-L176</a>
- Start line: `159`
- End line: `176`
- Signature:

```python
def get_active_pipeline_context() -> PipelineRunContext
```

### Internal relationship graph

### Public related functions

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Notebook template</summary>Reusable starter notebook workflow that shows how to run a FabricOps phase.</details>
- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
