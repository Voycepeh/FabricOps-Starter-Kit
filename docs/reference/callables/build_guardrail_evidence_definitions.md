# build_guardrail_evidence_definitions

Build catalogue evidence definitions for pipeline table guardrails.

## What this is for and when to use it

Build catalogue evidence definitions for pipeline table guardrails.

- Use inside pipeline guardrail orchestration to convert source or target table configs into catalogue evidence definitions.

## When not to use it

- Most notebook authors should not call this directly; use run_table_guardrails for normal 02_pipeline checks.

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
      <td data-label="Parameter"><code>table_configs</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source or target table configuration dictionaries. Each item must include ``key`` and normally includes ``table_name``, ``stage``, and optional target write metadata. DataFrame values are intentionally omitted from the returned definitions.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of catalogue evidence definitions keyed by table key with DataFrame values removed.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Pure helper; it does not read or write metadata.

## Related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../internal/pipeline__table_key/"><code>fabricops_kit.pipeline._table_key</code></a>
- <a href="../internal/pipeline__table_name/"><code>fabricops_kit.pipeline._table_name</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L124-L153">View build_guardrail_evidence_definitions on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def build_guardrail_evidence_definitions(table_configs: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Build catalogue evidence definitions for pipeline table guardrails.

    Parameters
    ----------
    table_configs : list of mapping
        Source or target table configuration dictionaries. Each item must
        include ``key`` and normally includes ``table_name``, ``stage``, and
        optional target write metadata. DataFrame values are intentionally
        omitted from the returned definitions.

    Returns
    -------
    dict[str, dict[str, Any]]
        Definitions keyed by table key, suitable for
        :func:`write_catalogue_evidence`. Target definitions include resolved
        write-layer, kind, and mode fields when the stage is ``target``.
    """
    definitions: dict[str, dict[str, Any]] = {}
    for table_config in table_configs:
        table_key = _table_key(table_config)
        definition = {key: value for key, value in table_config.items() if key != "df"}
        definition["table_name"] = _table_name(table_config)
        definition["stage"] = table_config.get("stage", "target")
        if definition["stage"] == "target":
            definition["layer"] = table_config.get("target_layer", "unified")
            definition["kind"] = table_config.get("target_kind", "lakehouse")
            definition["mode"] = table_config.get("write_mode", "overwrite")
        definitions[table_key] = definition
    return definitions
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.build_guardrail_evidence_definitions`
- Short name: `build_guardrail_evidence_definitions`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `124`
- Inbound references count: 1
- Outbound references count: 2

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail orchestration`.
- **inputs:** table_configs containing source or target table definitions and DataFrames.
- **output:** Dictionary of catalogue evidence definitions keyed by table key with DataFrame values removed.
- **side_effects:** Pure helper; it does not read or write metadata.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../internal/pipeline__table_key/"><code>fabricops_kit.pipeline._table_key</code></a>
- <a href="../internal/pipeline__table_name/"><code>fabricops_kit.pipeline._table_name</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L124-L153">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/pipeline.py#L124-L153</a>
- Start line: `124`
- End line: `153`
- Signature:

```python
def build_guardrail_evidence_definitions(table_configs: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Internal implementation helpers

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../internal/pipeline__table_key/"><code>fabricops_kit.pipeline._table_key</code></a>
- <a href="../internal/pipeline__table_name/"><code>fabricops_kit.pipeline._table_name</code></a>

</details>
