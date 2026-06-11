# write_lakehouse_table

## Purpose

Write a DataFrame to a configured Fabric lakehouse target.

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
      <td data-label="Details">Use when publishing a Spark DataFrame to a configured Fabric lakehouse table.</td>
    </tr>
    <tr>
      <td data-label="Item">Do not use when</td>
      <td data-label="Details">Do not use for metadata evidence tables unless the helper explicitly routes metadata, and do not use for warehouse tables.</td>
    </tr>
    <tr>
      <td data-label="Item">Example</td>
      <td data-label="Details">```python
write_lakehouse_table(curated_df, CONFIG, env="Sandbox", target="Unified", table="orders_curated", mode="overwrite")
```</td>
    </tr>
    <tr>
      <td data-label="Item">Errors</td>
      <td data-label="Details">Raises configuration, Spark, or write errors when the target cannot be resolved or the write fails.</td>
    </tr>
    <tr>
      <td data-label="Item">Side effects</td>
      <td data-label="Details">Writes data to a Fabric lakehouse table using the selected write mode.</td>
    </tr>
    <tr>
      <td data-label="Item">Related functions</td>
      <td data-label="Details">- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a><br>- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a><br>- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a></td>
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
      <td data-label="Meaning">Environment key such as `&quot;dev&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Logical target name such as `&quot;source&quot;` or `&quot;unified&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Target table name under the lakehouse `Tables` area.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>mode</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark write mode. Supported values are `&quot;append&quot;`, `&quot;overwrite&quot;`, `&quot;errorifexists&quot;`, and `&quot;ignore&quot;`.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>partition_by</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Column or columns used to physically partition the Delta table.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>repartition_by</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Optional repartitioning before write.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>overwrite_schema</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Whether to set Spark Delta `overwriteSchema=true` before saving.</td>
    </tr>
  </tbody>
</table>
</div>

## Returns

None; the DataFrame is written to the configured lakehouse table.

## Used by

- `fabricops_kit.data_agreement._ensure_metadata_tables`
- `fabricops_kit.data_agreement._write_row`
- `fabricops_kit.governance_review._review_governance_evidence`
- `fabricops_kit.governance_review._setup_governance_metadata_tables`
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- `fabricops_kit.metadata._register_current_notebook`
- `fabricops_kit.metadata._setup_notebook_registry_table`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

## Calls

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._registered_table_identifier`
- `fabricops_kit.fabric_input_output._uses_registered_metadata_table`

## Implementation details

### Call flow

```text
write_lakehouse_table(...)
├── _get_store(...)
├── _normalize_table_name(...)
├── _registered_table_identifier(...)
│   ├── _normalize_table_name(...)
│   └── _quote_identifier(...)
└── _uses_registered_metadata_table(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L227-L323">View write_lakehouse_table on GitHub</a>

```python
def write_lakehouse_table(
    df,
    config,
    env,
    target,
    table,
    mode="append",
    partition_by=None,
    repartition_by=None,
    overwrite_schema=True,
):
    """Write a Spark DataFrame to a Fabric lakehouse Delta table.

    This writes to the lakehouse `Tables/` area using the ABFSS root stored in
    a `FabricStore`. Use this in the Unified/Product stage after transformations,
    DQ checks, and runtime audit-column enrichment are complete.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment key such as `"dev"`.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    table : str
        Target table name under the lakehouse `Tables` area.
    mode : str, default "append"
        Spark write mode. Supported values are `"append"`, `"overwrite"`,
        `"errorifexists"`, and `"ignore"`.
    partition_by : str or list[str], optional
        Column or columns used to physically partition the Delta table.
    repartition_by : int, str, list, or tuple, optional
        Optional repartitioning before write.
    overwrite_schema : bool, default True
        Whether to set Spark Delta `overwriteSchema=true` before saving.

    Returns
    -------
    None
        The DataFrame is written to the target Delta table path.

    Notes
    -----
    Side effects:
    - Persists data to OneLake Delta storage under ``Tables/<table>``.
    - Optional repartitioning can change output file sizing and partition
      layout.

    Raises
    ------
    ValueError
        If `table` is missing, `mode` is invalid, or the resolved target is not a lakehouse.

    Examples
    --------
    >>> write_lakehouse_table(df, CONFIG, ENV, "unified", "CLEAN_ORDERS")
    """
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    table_name = _normalize_table_name(table)

    normalized_mode = str(mode or "").lower().strip()
    if normalized_mode not in {"append", "overwrite", "errorifexists", "ignore"}:
        raise ValueError("mode must be one of append, overwrite, errorifexists, ignore.")

    path = f"{store.root.rstrip('/')}/Tables/{table_name}"

    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            if len(repartition_by) > 0 and isinstance(repartition_by[0], int):
                df = df.repartition(repartition_by[0], *repartition_by[1:])
            else:
                df = df.repartition(*repartition_by)
        elif isinstance(repartition_by, int):
            df = df.repartition(repartition_by)
        else:
            df = df.repartition(repartition_by)

    writer = df.write.mode(normalized_mode).format("delta")

    if partition_by is not None:
        if isinstance(partition_by, (list, tuple)):
            writer = writer.partitionBy(*partition_by)
        else:
            writer = writer.partitionBy(partition_by)

    if overwrite_schema:
        writer = writer.option("overwriteSchema", "true")

    if _uses_registered_metadata_table(target):
        writer.saveAsTable(_registered_table_identifier(store, table_name))
    else:
        writer.save(path)
```

## Nested helper functions

??? info "Nested helper functions: 5"

    These helpers support `write_lakehouse_table` by handling shared implementation tasks reached from the public call flow; expand the source block only when you need maintainer-level details.

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
          <td data-label="Helper"><code>_normalize_table_name</code></td>
          <td data-label="Role">Return a safe Spark table name, never a nested folder path.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L81-L90"><code>src/fabricops_kit/fabric_input_output.py#L81-L90</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_registered_table_identifier</code></td>
          <td data-label="Role">Return a metadata lakehouse-qualified Spark table identifier.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L97-L99"><code>src/fabricops_kit/fabric_input_output.py#L97-L99</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_quote_identifier</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L93-L94"><code>src/fabricops_kit/fabric_input_output.py#L93-L94</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_uses_registered_metadata_table</code></td>
          <td data-label="Role">Return whether a target should use Spark table registration.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L102-L104"><code>src/fabricops_kit/fabric_input_output.py#L102-L104</code></a></td>
        </tr>
      </tbody>
    </table>

    ??? example "View helper source code"

        **`def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any`**

        Used by `write_lakehouse_table` through the implementation path shown above.

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

        **`def _normalize_table_name(table: str) -> str`**

        Used by `write_lakehouse_table` through the implementation path shown above.

        ```python
        def _normalize_table_name(table: str) -> str:
            """Return a safe Spark table name, never a nested folder path."""
            value = str(table or "").strip()
            if not value:
                raise ValueError("table is required.")
            if any(separator in value for separator in ("/", "\\")) or ".." in value:
                raise ValueError("table must be a table name, not a file path or nested folder path.")
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
                raise ValueError("table must contain only letters, numbers, and underscores, and must not start with a number.")
            return value
        ```

        **`def _registered_table_identifier(store: FabricStore, table: str) -> str`**

        Used by `write_lakehouse_table` through the implementation path shown above.

        ```python
        def _registered_table_identifier(store: FabricStore, table: str) -> str:
            """Return a metadata lakehouse-qualified Spark table identifier."""
            return f"{_quote_identifier(store.name)}.{_quote_identifier(_normalize_table_name(table))}"
        ```

        **`def _quote_identifier(identifier: str) -> str`**

        Used by `write_lakehouse_table` through the implementation path shown above.

        ```python
        def _quote_identifier(identifier: str) -> str:
            return f"`{str(identifier).replace('`', '``')}`"
        ```

        **`def _uses_registered_metadata_table(target: str) -> bool`**

        Used by `write_lakehouse_table` through the implementation path shown above.

        ```python
        def _uses_registered_metadata_table(target: str) -> bool:
            """Return whether a target should use Spark table registration."""
            return str(target or "").strip().lower() == "metadata"
        ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_lakehouse_table`
- Short name: `write_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `227`
- Inbound references count: 10
- Outbound references count: 4

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** df, config, env, target, table, optional schema, mode, and partitioning/write options.
- **output:** None; the DataFrame is written to the configured lakehouse table.
- **side_effects:** Writes data to a Fabric lakehouse table using the selected write mode.
- **failure_modes:** Raises configuration, Spark, or write errors when the target cannot be resolved or the write fails.
- **verification:** Verify upstream guardrails passed, confirm target routing from CONFIG, and check the intended write mode before generating code that calls this helper.

### Inbound references

- `fabricops_kit.data_agreement._ensure_metadata_tables`
- `fabricops_kit.data_agreement._write_row`
- `fabricops_kit.governance_review._review_governance_evidence`
- `fabricops_kit.governance_review._setup_governance_metadata_tables`
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- `fabricops_kit.metadata._register_current_notebook`
- `fabricops_kit.metadata._setup_notebook_registry_table`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Outbound references

- `fabricops_kit.config._get_store`
- `fabricops_kit.fabric_input_output._normalize_table_name`
- `fabricops_kit.fabric_input_output._registered_table_identifier`
- `fabricops_kit.fabric_input_output._uses_registered_metadata_table`

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L227-L323">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/fabric_input_output.py#L227-L323</a>
- Start line: `227`
- End line: `323`
- Signature:

```python
def write_lakehouse_table(df, config, env, target, table, mode='append', partition_by=None, repartition_by=None, overwrite_schema=True)
```

### Internal relationship graph

The human-readable implementation view above is the source of truth for public call flow, public callable source, and collapsed nested helper details.

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Call flow

```text
write_lakehouse_table(...)
├── _get_store(...)
├── _normalize_table_name(...)
├── _registered_table_identifier(...)
│   ├── _normalize_table_name(...)
│   └── _quote_identifier(...)
└── _uses_registered_metadata_table(...)
```

</details>
