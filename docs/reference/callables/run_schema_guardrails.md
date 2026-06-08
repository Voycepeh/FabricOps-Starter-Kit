# run_schema_guardrails

Run schema guardrails for many datasets using per-dataset presets.

## What this is for and when to use it

Run schema guardrails for many datasets using per-dataset presets.

- Use for source and target schema checks where each definition supplies expected_schema and schema_preset.

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
      <td data-label="Parameter"><code>datasets</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source or target DataFrames keyed by alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Definitions containing ``expected_schema`` and optional ``schema_preset`` values.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of schema guardrail results keyed by dataset alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L169-L195">View run_schema_guardrails on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def run_schema_guardrails(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Run schema guardrails for many datasets with per-dataset presets.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Source or target DataFrames keyed by alias.
    dataset_definitions : mapping of str to mapping
        Definitions containing ``expected_schema`` and optional
        ``schema_preset`` values.

    Returns
    -------
    dict[str, dict]
        Guardrail results keyed by dataset alias.
    """
    return {
        name: validate_schema(
            dataframe,
            dict(dataset_definitions[name].get("expected_schema") or {}),
            preset=str(dataset_definitions[name].get("schema_preset", "strict")),
        )
        for name, dataframe in datasets.items()
    }
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_schema_guardrails`
- Short name: `run_schema_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `169`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Schema guardrails`.
- **inputs:** datasets and dataset_definitions.
- **output:** Dictionary of schema guardrail results keyed by dataset alias.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L169-L195">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L169-L195</a>
- Start line: `169`
- End line: `195`
- Signature:

```python
def run_schema_guardrails(datasets: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]
```

### Internal relationship graph

### Public related functions

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

</details>
