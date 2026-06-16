# stop_if_failed

Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:907`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/guardrails.py#L907-L927">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use immediately after schema, freshness, profile behavior, or DQ guardrail helpers when can_continue controls whether the pipeline should proceed.

**Do not use when:**

- Do not use for informational warnings that should not block execution, or before a guardrail result exists.

**Additional context:**

Stops or raises for a blocking guardrail result so a notebook does not continue into unsafe downstream writes.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def stop_if_failed(result) -> None
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
schema_result = validate_schema(df, expected_schema)
stop_if_failed(schema_result)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `result` | `dict` | Yes | Direct schema, freshness, profile behavior, or DQ guardrail result. |

## Returns

None when execution may continue; otherwise raises or exits according to runtime behavior.

### Return interpretation

No return value means execution may continue. A blocking result raises or exits according to runtime settings.

## Raises / Errors

Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail must stop execution.

### Common failure causes

- The guardrail result is missing can_continue or status fields.
- A blocking guardrail returned can_continue as false.
- Notebook exit behavior is not supported in the current runtime.
- The caller passed a warning result that should not stop execution.

## Relationships

### Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.guardrails.SchemaDriftError`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

May terminate notebook execution through Fabric notebook utilities or raise an exception.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    stop_if_failed(...)
    └── SchemaDriftError(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `stop_if_failed` does not have package-local helper descendants in the generated call graph.

    <div class="reference-helper-groups">
      <section class="reference-helper-group reference-helper-group-empty">
        <h4>No internal helpers detected</h4>
        <p>This callable does not have package-local helper descendants in the generated call graph.</p>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.stop_if_failed`
- Short name: `stop_if_failed`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `907`
- Inbound references count: 1
- Outbound references count: 1
- Used in templates: 02_pipeline
- Glossary terms: guardrail, can_continue

### AI implementation contract

- **required_context:** Use in 02_pipeline after validate_schema, enforce_freshness, enforce_profile_behavior, or enforce_dq_rules and before write helpers.
- **inputs:** guardrail result dictionary and optional message/runtime controls.
- **output:** None when execution may continue; otherwise raises or exits according to runtime behavior.
- **side_effects:** May terminate notebook execution through Fabric notebook utilities or raise an exception.
- **failure_modes:** Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail must stop execution.
- **verification:** Verify the guardrail result shape includes status/can_continue/message before passing it to stop_if_failed.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.guardrails.SchemaDriftError`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/guardrails.py#L907-L927">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/guardrails.py#L907-L927</a>
- Start line: `907`
- End line: `927`
- Signature:

```python
def stop_if_failed(result) -> None
```

### Internal relationship graph

### Public related functions

- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
