# write_pipeline_targets

Write many target DataFrames using target definitions.

## What this is for and when to use it

Write many target DataFrames using target definitions.

- Use only after target schema, drift, and DQ guardrails have passed or warned according to policy.

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
      <td data-label="Parameter"><code>targets</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Target DataFrames keyed by alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Target definitions containing ``kind``, ``layer``, ``table_name``, and optional warehouse schema/write options.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">``00_env_config`` route configuration.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>default_mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Write mode used when a target does not specify ``mode``.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of target write statuses keyed by target alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Writes lakehouse or warehouse target tables through configured routes.

## Related functions

- <a href="../add_runtime_audit_columns/"><code>fabricops_kit.pipeline.add_runtime_audit_columns</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L445-L498">View write_pipeline_targets on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def write_pipeline_targets(
    targets: Mapping[str, Any],
    target_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    default_mode: str = "overwrite",
) -> dict[str, str]:
    """Write many target DataFrames to lakehouse or warehouse targets.

    Parameters
    ----------
    targets : mapping of str to DataFrame
        Target DataFrames keyed by alias.
    target_definitions : mapping of str to mapping
        Target definitions containing ``kind``, ``layer``, ``table_name``, and
        optional warehouse schema/write options.
    config : FrameworkConfig or dict
        ``00_env_config`` route configuration.
    env : str
        Environment key from ``00_env_config``.
    default_mode : str, default="overwrite"
        Write mode used when a target does not specify ``mode``.

    Returns
    -------
    dict[str, str]
        Write status keyed by target alias.
    """
    statuses: dict[str, str] = {}
    for name, dataframe in targets.items():
        definition = target_definitions[name]
        kind = str(definition.get("kind", "lakehouse")).lower()
        layer = str(definition.get("layer") or definition.get("target") or "product")
        table = _definition_name(name, definition)
        mode = str(definition.get("mode", default_mode))
        if kind == "lakehouse":
            write_lakehouse_table(
                dataframe,
                config,
                env,
                layer,
                table,
                mode=mode,
                partition_by=definition.get("partition_by"),
                repartition_by=definition.get("repartition_by"),
                overwrite_schema=bool(definition.get("overwrite_schema", mode == "overwrite")),
            )
        elif kind == "warehouse":
            write_warehouse_table(dataframe, config, env, layer, str(definition.get("schema", "dbo")), table, mode=mode)
        else:
            raise ValueError(f"Unsupported target kind for {name!r}: {kind!r}.")
        statuses[name] = "written"
    return statuses
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_pipeline_targets`
- Short name: `write_pipeline_targets`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `445`
- Inbound references count: 0
- Outbound references count: 3

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Target writes`.
- **inputs:** targets, target_definitions, config, env, and default_mode.
- **output:** Dictionary of target write statuses keyed by target alias.
- **side_effects:** Writes lakehouse or warehouse target tables through configured routes.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L445-L498">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L445-L498</a>
- Start line: `445`
- End line: `498`
- Signature:

```python
def write_pipeline_targets(targets: Mapping[str, Any], target_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, default_mode: str='overwrite') -> dict[str, str]
```

### Internal relationship graph

### Public related functions

- <a href="../add_runtime_audit_columns/"><code>fabricops_kit.pipeline.add_runtime_audit_columns</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Internal implementation helpers

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>
