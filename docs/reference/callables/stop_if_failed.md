# stop_if_failed

Stop a notebook only when a schema, stability, or DQ guardrail result blocks continuation.

## What this is for and when to use it

Stop a notebook only when a schema, stability, or DQ guardrail result blocks continuation.

- Use after schema, stability, or DQ guardrail helpers to stop the notebook when can_continue is false.

## When not to use it

- Do not use for informational warnings that should not block execution, or before a guardrail result exists.

## Example

```python
schema_result = validate_schema(df, expected_schema)
stop_if_failed(schema_result)
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>result</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Direct schema, catalogue stability, or DQ guardrail result.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

None when execution may continue; otherwise raises or exits according to runtime behavior.

## Errors and side effects

**Errors:** Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail must stop execution.

**Side effects:** May terminate notebook execution through Fabric notebook utilities or raise an exception.

## Related functions

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../internal/drift_SchemaDriftError/"><code>fabricops_kit.drift.SchemaDriftError</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/drift.py#L670-L689">View stop_if_failed on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def stop_if_failed(result) -> None:
    """Stop notebook execution when a guardrail result is blocking.

    Parameters
    ----------
    result : dict
        Direct schema, catalogue stability, or DQ guardrail result.

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

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.drift.stop_if_failed`
- Short name: `stop_if_failed`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source line: `670`
- Inbound references count: 1
- Outbound references count: 1

### AI implementation contract

- **required_context:** Use in 02_pipeline after validate_schema, enforce_catalogue_stability, or enforce_dq_rules and before write helpers.
- **inputs:** guardrail result dictionary and optional message/runtime controls.
- **output:** None when execution may continue; otherwise raises or exits according to runtime behavior.
- **side_effects:** May terminate notebook execution through Fabric notebook utilities or raise an exception.
- **failure_modes:** Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail must stop execution.
- **verification:** Verify the guardrail result shape includes status/can_continue/message before passing it to stop_if_failed.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../internal/drift_SchemaDriftError/"><code>fabricops_kit.drift.SchemaDriftError</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/drift.py#L670-L689">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/drift.py#L670-L689</a>
- Start line: `670`
- End line: `689`
- Signature:

```python
def stop_if_failed(result) -> None
```

### Internal relationship graph

### Public related functions

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

### Internal implementation helpers

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../internal/drift_SchemaDriftError/"><code>fabricops_kit.drift.SchemaDriftError</code></a>

</details>
