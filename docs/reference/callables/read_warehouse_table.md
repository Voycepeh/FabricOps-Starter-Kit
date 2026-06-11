# read_warehouse_table

Read a table from a configured Fabric warehouse target.

## What this is for and when to use it

Read a table from a configured Fabric warehouse target.

- Use when reading a table from a configured Fabric warehouse target.

## When not to use it

- Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or Excel paths.

## Example

```python
df = read_warehouse_table(CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders", spark_session=spark)
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
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark session to use. If omitted, the helper uses the notebook global `spark`.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Spark DataFrame loaded from the configured warehouse table.

## Errors and side effects

**Errors:** Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.

**Side effects:** Reads from a warehouse table; it does not write metadata, tables, or files.

## Related functions

- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/fabric_input_output.py#L323-L382">View read_warehouse_table on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None):
    """Read a table from a Microsoft Fabric warehouse.

    This uses Fabric Spark's `synapsesql` connector to read from a warehouse
    configured in the framework `CONFIG` mapping. In Source → Unified →
    Product workflows, this is commonly used when curated inputs are stored in
    Fabric Warehouse instead of Lakehouse tables.

    Parameters
    ----------
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
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the Fabric warehouse table.

    Raises
    ------
    RuntimeError
        If the Microsoft Fabric Spark connector is unavailable.
    ValueError
        If the selected environment or target is missing from the config.

    Examples
    --------
    >>> df = read_warehouse_table(CONFIG, ENV, "product", "dbo", "TABLE_NAME")
    """
    spark_obj = _get_spark(spark_session)
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

    return (
        spark_obj.read.option(Constants.WorkspaceId, store.workspace_id)
        .option(Constants.DatawarehouseId, store.item_id)
        .synapsesql(f"{store.name}.{schema}.{table}")
    )
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_warehouse_table`
- Short name: `read_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `323`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, schema, table, optional verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the configured warehouse table.
- **side_effects:** Reads from a warehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.
- **verification:** Verify the warehouse target/schema/table are configured and inspect the resulting DataFrame schema before downstream use.

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/fabric_input_output.py#L323-L382">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/fabric_input_output.py#L323-L382</a>
- Start line: `323`
- End line: `382`
- Signature:

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation helpers

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>

</details>
