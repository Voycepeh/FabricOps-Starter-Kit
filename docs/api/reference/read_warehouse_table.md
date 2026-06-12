# read_warehouse_table

Read a table from a configured Fabric warehouse target.

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when source data lives in a Fabric Warehouse rather than a lakehouse file or Delta table.

**Do not use when:**

- Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or Excel paths.

**Additional context:**

Reads data from a configured Fabric Warehouse table or query target into a Spark DataFrame.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_warehouse_table(CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment name in the config mapping, for example `"Sandbox"` or `"DE"`. |
| `target` | `str` | Yes | Warehouse target name under the selected environment, for example `"Warehouse"` or `"wh_Bronze"`. |
| `schema` | `str` | Yes | Warehouse schema name, for example `"dbo"`. |
| `table` | `str` | Yes | Warehouse table name. |
| `spark_session` | `object` | No | Spark session to use. If omitted, the helper uses the notebook global `spark`. |

## Returns

Spark DataFrame loaded from the configured warehouse table.

### Return interpretation

The returned DataFrame represents the warehouse read result; confirm filters and row counts before profiling or transformation.

## Raises / Errors

Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.

### Common failure causes

- The warehouse target is not configured.
- The table or SQL text is invalid.
- Warehouse connector context is unavailable.
- The caller lacks warehouse read permission.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._get_spark`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `00_env_config`
- `02_pipeline`
- `99_explore`

**Side effects:**

Reads from a warehouse table; it does not write metadata, tables, or files.

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    read_warehouse_table(...)
    ├── _get_spark(...)
    └── _get_store(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/fabric_input_output.py#L100-L130"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/config.py#L627-L667"><code>_get_store</code></a>
        </div>
      </section>
    </div>

    ??? example "View helper source by area"

        ??? example "Fabric or Spark access helpers"

            **`def _get_spark(spark_session=None)`**

            Source: [`src/fabricops_kit/fabric_input_output.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/fabric_input_output.py#L100-L130)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/config.py#L627-L667)

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


<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:338`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/fabric_input_output.py#L338-L397">View on GitHub</a>
</div>

??? example "Source code"

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

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_warehouse_table`
- Short name: `read_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `338`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 00_env_config, 02_pipeline, 99_explore
- Glossary terms: source table, notebook template

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/fabric_input_output.py#L338-L397">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/fabric_input_output.py#L338-L397</a>
- Start line: `338`
- End line: `397`
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
- Grouped helper summary and optional source snippets are rendered in the page-level Implementation details section.

</details>

## Source link

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:338`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/49b66befe4534bc43d6bccbed2445ec23dd02d36/src/fabricops_kit/fabric_input_output.py#L338-L397">View on GitHub</a>
</div>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
