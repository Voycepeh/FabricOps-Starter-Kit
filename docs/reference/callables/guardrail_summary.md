# guardrail_summary

Return a concise display summary for table guardrail results.

## What this is for and when to use it

Return a concise display summary for table guardrail results.

- Use after run_table_guardrails to display schema, stability, DQ, catalogue, and failed-table results without exposing internal profile objects.

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
      <td data-label="Meaning">Result bundle returned by :func:`run_table_guardrails`.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary containing schema_results, stability_results, dq_results, catalogue_status, and failed_tables.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Pure formatting helper; it does not display by itself or write metadata.

## Related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L310-L330">View guardrail_summary on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def guardrail_summary(guardrail_results: Mapping[str, Any]) -> dict[str, Any]:
    """Return a concise notebook display summary for guardrail results.

    Parameters
    ----------
    guardrail_results : mapping
        Result bundle returned by :func:`run_table_guardrails`.

    Returns
    -------
    dict[str, Any]
        Concise summary containing schema, stability, DQ, catalogue, and failed
        table information for notebook display.
    """
    return {
        "schema_results": guardrail_results["schema_results"],
        "stability_results": guardrail_results["stability_results"],
        "dq_results": guardrail_results["dq_results"],
        "catalogue_status": guardrail_results["catalogue_status"],
        "failed_tables": guardrail_results["failed_tables"],
    }
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.guardrail_summary`
- Short name: `guardrail_summary`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `310`
- Inbound references count: 0
- Outbound references count: 0

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail summary`.
- **inputs:** guardrail_results returned by run_table_guardrails.
- **output:** Dictionary containing schema_results, stability_results, dq_results, catalogue_status, and failed_tables.
- **side_effects:** Pure formatting helper; it does not display by itself or write metadata.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L310-L330">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L310-L330</a>
- Start line: `310`
- End line: `330`
- Signature:

```python
def guardrail_summary(guardrail_results: Mapping[str, Any]) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Internal implementation helpers

Not documented yet

</details>
