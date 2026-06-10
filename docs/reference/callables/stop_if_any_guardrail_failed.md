# stop_if_any_guardrail_failed

Stop notebook execution when any table guardrail is blocking.

## What this is for and when to use it

Stop notebook execution when any table guardrail is blocking.

- Use immediately after displaying source or target guardrail results to block transformation or writes when any table cannot continue.

## When not to use it

- Not documented yet

## Example

```python
Not documented yet
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
      <td data-label="Parameter"><code>guardrail_results</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Result bundle returned by :func:`run_table_guardrails`. The helper checks ``can_continue`` and forwards a standard failed guardrail result to :func:`fabricops_kit.drift.stop_if_failed` when one or more tables failed.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

None when all guardrails can continue; raises through stop_if_failed for blocking failures.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** May stop notebook execution by delegating to stop_if_failed.

## Related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../guardrail_summary/"><code>fabricops_kit.pipeline.guardrail_summary</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L333-L361">View stop_if_any_guardrail_failed on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def stop_if_any_guardrail_failed(guardrail_results: Mapping[str, Any]) -> None:
    """Stop notebook execution when any table guardrail is blocking.

    Parameters
    ----------
    guardrail_results : mapping
        Result bundle returned by :func:`run_table_guardrails`. The helper
        checks ``can_continue`` and forwards a standard failed guardrail result
        to :func:`fabricops_kit.drift.stop_if_failed` when one or more tables
        failed.

    Returns
    -------
    None
        Returns normally when all guardrails can continue. Raises through
        :func:`stop_if_failed` for blocking failures.
    """
    if guardrail_results.get("can_continue", True):
        return

    failed_tables = guardrail_results.get("failed_tables", [])
    stop_if_failed(
        {
            "status": "failed",
            "can_continue": False,
            "message": "Blocking guardrail failure for table(s): " + ", ".join(failed_tables),
            "failed_tables": failed_tables,
        }
    )
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.stop_if_any_guardrail_failed`
- Short name: `stop_if_any_guardrail_failed`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `333`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail stopping`.
- **inputs:** guardrail_results returned by run_table_guardrails.
- **output:** None when all guardrails can continue; raises through stop_if_failed for blocking failures.
- **side_effects:** May stop notebook execution by delegating to stop_if_failed.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L333-L361">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L333-L361</a>
- Start line: `333`
- End line: `361`
- Signature:

```python
def stop_if_any_guardrail_failed(guardrail_results: Mapping[str, Any]) -> None
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../guardrail_summary/"><code>fabricops_kit.pipeline.guardrail_summary</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

</details>
