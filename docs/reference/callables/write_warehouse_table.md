# write_warehouse_table

Write a DataFrame to a configured Fabric warehouse target.

## Purpose

Write a DataFrame to a configured Fabric warehouse target.

## At a glance

**Use when:**

- Use when publishing a Spark DataFrame to a configured Fabric warehouse table.

**Do not use when:**

- Do not use for lakehouse table writes, lakehouse Files writes, or metadata evidence writes.

**Example:**

```python
write_warehouse_table(serving_df, CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders_serving", mode="append")
```

**Errors:**

Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.

**Side effects:**

Writes data to a Fabric warehouse table using the selected mode.

## Used by

Not documented yet

## Calls

- `fabricops_kit.config._get_store`

## Callable implementation

### Function details

- Module: `fabric_input_output`
- Classification: Callable
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `433`
- Signature:

```python
def write_warehouse_table(df, config, env, target, schema, table, mode='append')
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
      <td data-label="Parameter"><code>df</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark DataFrame to write.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">FabricOps FrameworkConfig or compatible config object.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment name in the config mapping, for example `&quot;Sandbox&quot;` or `&quot;DE&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Warehouse target name under the selected environment, for example `&quot;Warehouse&quot;` or `&quot;wh_Bronze&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>schema</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Warehouse schema name, for example `&quot;dbo&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Warehouse table name.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark write mode, for example `&quot;append&quot;` or `&quot;overwrite&quot;`.</td>
    </tr>
  </tbody>
</table>
</div>

### Returns

None; the DataFrame is written to the configured warehouse table.

### Notes

Side effect: performs a write operation to the target warehouse object via
Fabric runtime connector APIs.

### Public callable source code

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/fabric_input_output.py#L433-L497">View write_warehouse_table on GitHub</a>

```python
def write_warehouse_table(df, config, env, target, schema, table, mode="append"):
    """Write a Spark DataFrame to a Microsoft Fabric warehouse table.

    This uses Fabric Spark's `synapsesql` connector to write to a warehouse
    configured in the framework `CONFIG` mapping. Use this near the end of the
    Product step when publishing serving tables.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment name in the config mapping, for example `"Sandbox"` or `"DE"`.
    target : str
        Warehouse target name under the selected environment, for example
        `"Warehouse"` or `"wh_Bronze"`.
    schema : str
        Warehouse schema name, for example `"dbo"`.
    table : str
        Warehouse table name.
    mode : str, default "append"
        Spark write mode, for example `"append"` or `"overwrite"`.

    Returns
    -------
    None
        The DataFrame is written to the target warehouse table.

    Notes
    -----
    Side effect: performs a write operation to the target warehouse object via
    Fabric runtime connector APIs.

    Raises
    ------
    RuntimeError
        If the Microsoft Fabric Spark connector is unavailable.
    ValueError
        If the selected environment or target is missing from the config.

    Examples
    --------
    >>> write_warehouse_table(df, CONFIG, ENV, "product", "dbo", "TABLE_NAME")
    """
    store = _get_store(config, env, target)
    if store.kind != "warehouse":
        raise ValueError(f"Target '{env}/{target}' is not a warehouse store.")

    try:
        import com.microsoft.spark.fabric
        from com.microsoft.spark.fabric.Constants import Constants
    except Exception as exc:
        raise RuntimeError(
            "This function must run inside Microsoft Fabric Spark with "
            "com.microsoft.spark.fabric available."
        ) from exc

    (
        df.write.mode(mode)
        .option(Constants.WorkspaceId, store.workspace_id)
        .option(Constants.DatawarehouseId, store.item_id)
        .synapsesql(f"{store.name}.{schema}.{table}")
    )
```

## Internal implementation summary

??? info "Call flow"

    ```text
    write_warehouse_table(...)
    └── _get_store(...)
    ```

??? info "Internal helpers used: 1"

    This callable uses 1 internal helpers for fabric or spark access.

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
          <td data-label="Area">Fabric or Spark access</td>
          <td data-label="Helpers"><code>_get_store</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Fabric or Spark access helpers"

            **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/config.py#L627-L667)

            ```python
            def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any:
                """Resolve a configured Fabric path for an environment and target.

                Parameters
                ----------
                env : str
                    Environment key such as ``Sandbox``, ``DE``, or ``Prod``.
                target : str
                    Target key such as ``Source``, ``Unified``, ``Product``, or ``Warehouse``.
                config : FrameworkConfig | PathConfig | None
                    Configuration that contains environment-to-target path mappings.

                Returns
                -------
                Any
                    FabricStore object with ``workspace_id``, ``house_id``, ``house_name``, and ``root``.

                Raises
                ------
                ValueError
                    If config is missing, or if the environment/target mapping does not exist.

                Examples
                --------
                >>> get_path("Sandbox", "Source", config=CONFIG)
                Housepath(...)
                """
                if config is None:
                    raise ValueError("No Fabric config was provided. Pass a FrameworkConfig or PathConfig instance.")
                paths = config.path_config.paths if isinstance(config, FrameworkConfig) else config.paths
                if env not in paths:
                    available_envs = ", ".join(sorted(paths.keys())) or "<none>"
                    raise ValueError(
                        f"Environment '{env}' was not found in Fabric config. Available environments: {available_envs}."
                    )
                if target not in paths[env]:
                    available_targets = ", ".join(sorted(paths[env].keys())) or "<none>"
                    raise ValueError(
                        f"Target '{target}' was not found under environment '{env}'. Available targets: {available_targets}."
                    )
                return paths[env][target]
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_warehouse_table`
- Short name: `write_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `433`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** df, config, env, target, schema, table, and write mode.
- **output:** None; the DataFrame is written to the configured warehouse table.
- **side_effects:** Writes data to a Fabric warehouse table using the selected mode.
- **failure_modes:** Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.
- **verification:** Verify guardrails passed, confirm schema/table routing from CONFIG, and check the intended write mode before calling.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config._get_store`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/fabric_input_output.py#L433-L497">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1a340ba809c58f40e81214f59b2f021ee1bdadba/src/fabricops_kit/fabric_input_output.py#L433-L497</a>
- Start line: `433`
- End line: `497`
- Signature:

```python
def write_warehouse_table(df, config, env, target, schema, table, mode='append')
```

### Internal relationship graph

### Public related functions

- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 1
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
