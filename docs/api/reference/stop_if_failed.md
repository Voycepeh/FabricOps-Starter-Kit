# stop_if_failed

Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.

## Purpose

Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.

## At a glance

**Use when:**

- Use after schema, freshness, profile behavior, or DQ guardrail helpers to stop the notebook when can_continue is false.

**Do not use when:**

- Do not use for informational warnings that should not block execution, or before a guardrail result exists.

**Example:**

```python
schema_result = validate_schema(df, expected_schema)
stop_if_failed(schema_result)
```

**Errors:**

Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail must stop execution.

**Side effects:**

May terminate notebook execution through Fabric notebook utilities or raise an exception.

## Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Calls

- `fabricops_kit.guardrails.SchemaDriftError`

## Callable implementation

### Function details

- Module: `guardrails`
- Classification: Callable
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `840`
- Signature:

```python
def stop_if_failed(result) -> None
```

### Parameters

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
      <td data-label="Meaning">Direct schema, freshness, profile behavior, or DQ guardrail result.</td>
    </tr>
  </tbody>
</table>
</div>

### Returns

None when execution may continue; otherwise raises or exits according to runtime behavior.

### Notes

No additional callable notes are documented.

### Public callable source code

- Source file path: `src/fabricops_kit/guardrails.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L840-L859">View stop_if_failed on GitHub</a>

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

## Internal implementation summary

??? info "Call flow"

    ```text
    stop_if_failed(...)
    └── SchemaDriftError(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `stop_if_failed` does not have package-local helper descendants in the generated call graph.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">—</td>
          <td data-label="Helpers">—</td>
          <td data-label="What they do">No internal helpers detected.</td>
        </tr>
      </tbody>
    </table>
    </div>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L840-L859">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L840-L859</a>
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
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
