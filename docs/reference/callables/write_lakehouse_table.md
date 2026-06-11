# write_lakehouse_table

Write a DataFrame to a configured Fabric lakehouse target.

## What this is for and when to use it

Write a DataFrame to a configured Fabric lakehouse target.

- Use when publishing a Spark DataFrame to a configured Fabric lakehouse table.

## When not to use it

- Do not use for metadata evidence tables unless the helper explicitly routes metadata, and do not use for warehouse tables.

## Example

```python
write_lakehouse_table(curated_df, CONFIG, env="Sandbox", target="Unified", table="orders_curated", mode="overwrite")
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

## Output

None; the DataFrame is written to the configured lakehouse table.

## Errors and side effects

**Errors:** Raises configuration, Spark, or write errors when the target cannot be resolved or the write fails.

**Side effects:** Writes data to a Fabric lakehouse table using the selected write mode.

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__lakehouse_table_identifier/"><code>fabricops_kit.fabric_input_output._lakehouse_table_identifier</code></a>
- <a href="../internal/fabric_input_output__normalize_table_name/"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></a>
- <a href="../internal/fabric_input_output__use_registered_table/"><code>fabricops_kit.fabric_input_output._use_registered_table</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/fabric_input_output.py#L232-L333">View write_lakehouse_table on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

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
    a `FabricStore`. For the configured ``metadata`` target, it writes through
    Spark table registration with ``saveAsTable`` against the metadata
    lakehouse name, preventing ambiguous nested Delta paths. Use this in the
    Unified/Product stage after transformations, DQ checks, and runtime
    audit-column enrichment are complete.

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
    - For the ``metadata`` target, registers or appends to a Spark catalog table
      in the configured metadata lakehouse.
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

    if _use_registered_table(target):
        writer.saveAsTable(_lakehouse_table_identifier(store, table_name))
    else:
        writer.save(path)
```

</details>

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
- Source line: `232`
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

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>

### Outbound references

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__lakehouse_table_identifier/"><code>fabricops_kit.fabric_input_output._lakehouse_table_identifier</code></a>
- <a href="../internal/fabric_input_output__normalize_table_name/"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></a>
- <a href="../internal/fabric_input_output__use_registered_table/"><code>fabricops_kit.fabric_input_output._use_registered_table</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/fabric_input_output.py#L232-L333">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/fabric_input_output.py#L232-L333</a>
- Start line: `232`
- End line: `333`
- Signature:

```python
def write_lakehouse_table(df, config, env, target, table, mode='append', partition_by=None, repartition_by=None, overwrite_schema=True)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>
- <a href="../write_pipeline_lineage/"><code>fabricops_kit.pipeline.write_pipeline_lineage</code></a>
- <a href="../write_pipeline_run_summary/"><code>fabricops_kit.pipeline.write_pipeline_run_summary</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__lakehouse_table_identifier/"><code>fabricops_kit.fabric_input_output._lakehouse_table_identifier</code></a>
- <a href="../internal/fabric_input_output__normalize_table_name/"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></a>
- <a href="../internal/fabric_input_output__use_registered_table/"><code>fabricops_kit.fabric_input_output._use_registered_table</code></a>

</details>
