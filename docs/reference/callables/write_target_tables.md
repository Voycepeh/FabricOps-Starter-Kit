# write_target_tables

Write checked target DataFrames from TARGET_TABLES to Fabric targets.

## What this is for and when to use it

Write checked target DataFrames from TARGET_TABLES to Fabric targets.

- Use after target guardrails pass to write the checked or DQ-annotated DataFrame held in each target config.

## When not to use it

- Do not call before stop_if_any_guardrail_failed has validated target guardrail results.

## Example

```python
target_write_status = write_target_tables(TARGET_TABLES, CONFIG, ENV_NAME)
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
      <td data-label="Parameter"><code>target_table_configs</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Enriched target configs, normally returned by :func:`prepare_target_table_configs` and updated by :func:`run_table_guardrails`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">FabricOps framework configuration from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key used for configured target routing.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Write status dictionary keyed by target key.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Writes Lakehouse or Warehouse target tables through configured Fabric targets.

## Related functions

- <a href="../prepare_target_table_configs/"><code>fabricops_kit.pipeline.prepare_target_table_configs</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L281-L334">View write_target_tables on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def write_target_tables(target_table_configs: list[Mapping[str, Any]], config: Any, env: str) -> dict[str, str]:
    """Write checked target DataFrames to configured Lakehouse or Warehouse targets.

    Parameters
    ----------
    target_table_configs : list of mapping
        Enriched target configs, normally returned by
        :func:`prepare_target_table_configs` and updated by
        :func:`run_table_guardrails`.
    config : Any
        FabricOps framework configuration from ``00_env_config``.
    env : str
        Environment key used for configured target routing.

    Returns
    -------
    dict[str, str]
        Write status keyed by target config ``key``.
    """
    target_write_status: dict[str, str] = {}
    for target_config in target_table_configs:
        target_key = target_config["key"]
        target_df = target_config["df"]
        target_kind = str(target_config.get("target_kind", target_config.get("kind", "lakehouse"))).lower()
        target_layer = target_config.get("target_layer", target_config.get("layer", "unified"))
        target_table = target_config.get("target_name", target_config.get("table_name", target_key))
        target_mode = target_config.get("write_mode", target_config.get("mode", "overwrite"))

        if target_kind == "lakehouse":
            write_lakehouse_table(
                target_df,
                config,
                env,
                target_layer,
                target_table,
                mode=target_mode,
                partition_by=target_config.get("partition_by"),
                repartition_by=target_config.get("repartition_by"),
                overwrite_schema=target_config.get("overwrite_schema", target_mode == "overwrite"),
            )
        elif target_kind == "warehouse":
            write_warehouse_table(
                target_df,
                config,
                env,
                target_layer,
                target_config.get("schema", "dbo"),
                target_table,
                mode=target_mode,
            )
        else:
            raise ValueError(f"Unsupported target kind for {target_key}: {target_kind}")
        target_write_status[target_key] = "written"
    return target_write_status
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.write_target_tables`
- Short name: `write_target_tables`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `281`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Uses CONFIG and env from 00_env_config and supports lakehouse and warehouse target kinds.
- **inputs:** target_table_configs, config, and env.
- **output:** Write status dictionary keyed by target key.
- **side_effects:** Writes Lakehouse or Warehouse target tables through configured Fabric targets.
- **failure_modes:** Not documented yet
- **verification:** Verify target_kind, target_layer, target_name, write_mode, and optional partition/write settings match the intended Fabric target.

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L281-L334">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L281-L334</a>
- Start line: `281`
- End line: `334`
- Signature:

```python
def write_target_tables(target_table_configs: list[Mapping[str, Any]], config: Any, env: str) -> dict[str, str]
```

### Internal relationship graph

### Public related functions

- <a href="../prepare_target_table_configs/"><code>fabricops_kit.pipeline.prepare_target_table_configs</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>

### Internal implementation helpers

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>

</details>
