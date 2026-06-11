# read_warehouse_table

## Purpose

Read a table from a configured Fabric warehouse target.

## At a glance

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Item</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Item">Use when</td>
      <td data-label="Details">Use when reading a table from a configured Fabric warehouse target.</td>
    </tr>
    <tr>
      <td data-label="Item">Do not use when</td>
      <td data-label="Details">Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or Excel paths.</td>
    </tr>
    <tr>
      <td data-label="Item">Example</td>
      <td data-label="Details">```python
df = read_warehouse_table(CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders", spark_session=spark)
```</td>
    </tr>
    <tr>
      <td data-label="Item">Errors</td>
      <td data-label="Details">Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.</td>
    </tr>
    <tr>
      <td data-label="Item">Side effects</td>
      <td data-label="Details">Reads from a warehouse table; it does not write metadata, tables, or files.</td>
    </tr>
    <tr>
      <td data-label="Item">Related functions</td>
      <td data-label="Details">- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a><br>- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a></td>
    </tr>
  </tbody>
</table>
</div>

## Parameters

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

## Returns

Spark DataFrame loaded from the configured warehouse table.

## Used by

No public or package-local callers detected by the generated dependency graph.

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`

## Implementation details

### Call flow

```text
read_warehouse_table(...)
├── _get_spark(...)
└── _get_store(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L371-L430">View read_warehouse_table on GitHub</a>

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

## Nested helper functions

??? info "Nested helper functions: 2"

    These helpers support `read_warehouse_table` by handling shared implementation tasks reached from the public call flow; expand the source block only when you need maintainer-level details.

    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Helper</th>
          <th>Role</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Helper"><code>_get_store</code></td>
          <td data-label="Role">Resolve a configured Fabric path for an environment and target.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L618-L658"><code>src/fabricops_kit/config.py#L618-L658</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_get_spark</code></td>
          <td data-label="Role">Return an explicit Spark session or the active notebook global `spark`.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L125-L155"><code>src/fabricops_kit/fabric_input_output.py#L125-L155</code></a></td>
        </tr>
      </tbody>
    </table>

    ??? example "View helper source code"

        **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

        Used by `read_warehouse_table` through the implementation path shown above.

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

        **`def _get_spark(spark_session=None)`**

        Used by `read_warehouse_table` through the implementation path shown above.

        ```python
        def _get_spark(spark_session=None):
            """Return an explicit Spark session or the active notebook global `spark`.

            Most Fabric notebooks already expose a global `spark` object. Tests and
            local scripts can pass `spark_session` explicitly to avoid relying on the
            notebook runtime.

            Parameters
            ----------
            spark_session : object, optional
                Spark session to use instead of the notebook global `spark`.

            Returns
            -------
            object
                Spark session object.

            Raises
            ------
            RuntimeError
                If no Spark session is passed and no global `spark` object exists.
            """
            if spark_session is not None:
                return spark_session
            try:
                return globals()["spark"]
            except KeyError as exc:
                raise RuntimeError(
                    "Spark session was not provided and global 'spark' was not found. "
                    "Run this inside Fabric/Spark or pass spark_session explicitly."
                ) from exc
        ```


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
- Source line: `371`
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

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L371-L430">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L371-L430</a>
- Start line: `371`
- End line: `430`
- Signature:

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

### Internal relationship graph

The human-readable implementation view above is the source of truth for public call flow, public callable source, and collapsed nested helper details.

### Public related functions

- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Call flow

```text
read_warehouse_table(...)
├── _get_spark(...)
└── _get_store(...)
```

</details>
