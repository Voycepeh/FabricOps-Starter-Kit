# read_warehouse_table

Read a table from a configured Fabric warehouse target.

## Purpose

This API reference documents the callable summarized above. Use the sections below for when to use it, inputs, return values, template usage, and implementation details.

## When to use this

- Use when reading a table from a configured Fabric warehouse target.

## At a glance

**Do not use when:**

- Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or Excel paths.

**Errors:**

Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.

**Side effects:**

Reads from a warehouse table; it does not write metadata, tables, or files.

## Used in templates

- `00_env_config`
- `02_pipeline`
- `99_explore`

## Used by

Not documented yet

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`

## Function details and source

### Function details

- Module: `fabric_input_output`
- Classification: Callable
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `371`
- Signature:

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

### Parameters

`config` : `FrameworkConfig | dict`, required
: FabricOps FrameworkConfig or compatible config object.

`env` : `str`, required
: Environment name in the config mapping, for example `"Sandbox"` or `"DE"`.

`target` : `str`, required
: Warehouse target name under the selected environment, for example `"Warehouse"` or `"wh_Bronze"`.

`schema` : `str`, required
: Warehouse schema name, for example `"dbo"`.

`table` : `str`, required
: Warehouse table name.

`spark_session` : `object`, optional
: Spark session to use. If omitted, the helper uses the notebook global `spark`.

### Returns

Spark DataFrame loaded from the configured warehouse table.

### Return interpretation

Interpret the returned value according to the Returns section above.

### Common failure causes

No common failure causes are documented beyond the Errors section.

### Notes

No additional callable notes are documented.

### Example

```python
df = read_warehouse_table(CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders", spark_session=spark)
```

### Public callable source code

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L371-L430">View read_warehouse_table on GitHub</a>

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

## Internal implementation summary

??? info "Call flow"

    ```text
    read_warehouse_table(...)
    ├── _get_spark(...)
    └── _get_store(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for fabric or spark access.

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
          <td data-label="Helpers"><code>_get_spark</code>, <code>_get_store</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Fabric or Spark access helpers"

            **`def _get_spark(spark_session=None)`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L125-L155)

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

            **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L627-L667)

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

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_warehouse_table`
- Short name: `read_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `371`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 00_env_config, 02_pipeline, 99_explore
- Glossary terms: —

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L371-L430">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/fabric_input_output.py#L371-L430</a>
- Start line: `371`
- End line: `430`
- Signature:

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
