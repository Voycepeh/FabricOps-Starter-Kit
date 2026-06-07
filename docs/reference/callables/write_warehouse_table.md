# write_warehouse_table

Write a DataFrame to a configured Fabric warehouse target.

## Use this when

Use when publishing a Spark DataFrame to a configured Fabric warehouse table.

## Do not use this for

Do not use for lakehouse table writes, lakehouse Files writes, or metadata evidence writes.

## Example

```python
write_warehouse_table(serving_df, CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders_serving", mode="append")
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>What it means</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>df</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Spark DataFrame to write.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">FabricOps FrameworkConfig or compatible config object.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Environment name in the config mapping, for example `&quot;Sandbox&quot;` or `&quot;DE&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Warehouse target name under the selected environment, for example `&quot;Warehouse&quot;` or `&quot;wh_Bronze&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>schema</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Warehouse schema name, for example `&quot;dbo&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Warehouse table name.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="What it means">Spark write mode, for example `&quot;append&quot;` or `&quot;overwrite&quot;`.</td>
    </tr>
  </tbody>
</table>
</div>

<details class="reference-signature-details">
<summary>Full signature</summary>

```python
def write_warehouse_table(df, config, env, target, schema, table, mode='append')
```

</details>

## Output

None; the DataFrame is written to the configured warehouse table.

## Raises

Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.

## Side effects

Writes data to a Fabric warehouse table using the selected mode.

## Related functions

- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>

</details>

<details class="reference-metadata-details">
<summary>AI implementation contract</summary>

These fields are generated for agents and maintainers, not for quick-start reading.

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** df, config, env, target, schema, table, and write mode.
- **output:** None; the DataFrame is written to the configured warehouse table.
- **side_effects:** Writes data to a Fabric warehouse table using the selected mode.
- **failure_modes:** Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.
- **verification:** Verify guardrails passed, confirm schema/table routing from CONFIG, and check the intended write mode before calling.

</details>

<details class="reference-metadata-details">
<summary>Function manifest</summary>

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_warehouse_table`
- Short name: `write_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `385`
- Inbound references count: 0
- Outbound references count: 1

</details>

<details class="reference-metadata-details">
<summary>Raw inbound and outbound references</summary>

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>

</details>

## Source code

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b6a5693130e525f919566c2115ac67da9c6faef/src/fabricops_kit/fabric_input_output.py#L385-L449">View write_warehouse_table on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

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

</details>
