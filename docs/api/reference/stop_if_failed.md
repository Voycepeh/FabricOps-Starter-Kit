# stop_if_failed

Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.

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

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:840`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/guardrails.py#L840-L859">View on GitHub</a>
</div>

??? example "Source code"

    ```python
    def stop_if_failed(result) -> None:
        """Stop notebook execution when a guardrail result is blocking.

        Parameters
        ----------
        result : dict
            Direct schema, freshness, profile behavior, or DQ guardrail result.

        Raises
        ------
        SchemaDriftError
            If the resolved result has ``can_continue=False``.
        """
        resolved = (result or {}).get("result") if isinstance(result, dict) and "result" in result else result
        resolved = resolved or {}
        if bool(resolved.get("can_continue", True)):
            return
        status = resolved.get("status", "failed")
        detail = resolved.get("message") or resolved.get("summary") or "Guardrail blocked execution."
        raise SchemaDriftError(f"Guardrail blocked execution with status: {status}. {detail}")
    ```

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
- Source line: `840`
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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/guardrails.py#L840-L859">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/guardrails.py#L840-L859</a>
- Start line: `840`
- End line: `859`
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
- Grouped helper summary and optional source snippets are rendered in the page-level Implementation details section.

</details>

## Source link

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:840`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/guardrails.py#L840-L859">View on GitHub</a>
</div>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
