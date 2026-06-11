# read_lakehouse_table

Read a table from a configured Fabric lakehouse target.

## What this is for and when to use it

Read a table from a configured Fabric lakehouse target.

- Use when reading a Delta table from a configured Fabric lakehouse target.

## When not to use it

- Do not use for lakehouse Files CSV, Parquet, or Excel paths, or for warehouse SQL tables.

## Example

```python
df = read_lakehouse_table(CONFIG, env="Sandbox", target="Source", table="orders", spark_session=spark)
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
      <td data-label="Meaning">Table name under the lakehouse `Tables` area.</td>
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

Spark DataFrame loaded from the configured lakehouse table.

## Errors and side effects

**Errors:** Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.

**Side effects:** Reads from a lakehouse table; it does not write metadata, tables, or files.

## Related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/governance_review__read_metadata_rows/"><code>fabricops_kit.governance_review._read_metadata_rows</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__current_database_matches/"><code>fabricops_kit.fabric_input_output._current_database_matches</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__normalize_table_name/"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></a>
- <a href="../internal/fabric_input_output__registered_table_identifier/"><code>fabricops_kit.fabric_input_output._registered_table_identifier</code></a>
- <a href="../internal/fabric_input_output__uses_registered_metadata_table/"><code>fabricops_kit.fabric_input_output._uses_registered_metadata_table</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/fabric_input_output.py#L171-L224">View read_lakehouse_table on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def read_lakehouse_table(config, env, target, table, spark_session=None):
    """Read a Delta table from a Fabric lakehouse.

    This reads from the lakehouse `Tables/` area using the ABFSS root stored in
    a `FabricStore`. In the notebook lifecycle, call this near the start of the
    Source or Unified step when loading Delta-backed source datasets.

    Parameters
    ----------
    config : FrameworkConfig | dict
        FabricOps FrameworkConfig or compatible config object.
    env : str
        Environment key such as `"dev"`.
    target : str
        Logical target name such as `"source"` or `"unified"`.
    table : str
        Table name under the lakehouse `Tables` area.
    spark_session : object, optional
        Spark session to use. If omitted, the helper uses the notebook global
        `spark`.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the Delta table.

    Raises
    ------
    ValueError
        If `table` is missing or the resolved target is not a lakehouse.
    RuntimeError
        If no Spark session is available.

    Examples
    --------
    >>> df = read_lakehouse_table(CONFIG, ENV, "source", "RAW_ORDERS")
    """
    store = _get_store(config, env, target)
    if store.kind != "lakehouse":
        raise ValueError(f"Target '{env}/{target}' is not a lakehouse store.")
    table_name = _normalize_table_name(table)

    spark_obj = _get_spark(spark_session)
    if _uses_registered_metadata_table(target):
        try:
            return spark_obj.table(_registered_table_identifier(store, table_name))
        except Exception:
            if _current_database_matches(spark_obj, store):
                try:
                    return spark_obj.table(table_name)
                except Exception:
                    pass
    path = f"{store.root.rstrip('/')}/Tables/{table_name}"
    return spark_obj.read.format("delta").load(path)
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_table`
- Short name: `read_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `171`
- Inbound references count: 11
- Outbound references count: 6

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, table, optional schema, verbose flag, and spark_session.
- **output:** Spark DataFrame loaded from the configured lakehouse table.
- **side_effects:** Reads from a lakehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.
- **verification:** Verify the target/table name comes from CONFIG and check the returned DataFrame schema or row count before downstream transformations.

### Inbound references

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/governance_review__read_metadata_rows/"><code>fabricops_kit.governance_review._read_metadata_rows</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

### Outbound references

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__current_database_matches/"><code>fabricops_kit.fabric_input_output._current_database_matches</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__normalize_table_name/"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></a>
- <a href="../internal/fabric_input_output__registered_table_identifier/"><code>fabricops_kit.fabric_input_output._registered_table_identifier</code></a>
- <a href="../internal/fabric_input_output__uses_registered_metadata_table/"><code>fabricops_kit.fabric_input_output._uses_registered_metadata_table</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/fabric_input_output.py#L171-L224">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/fabric_input_output.py#L171-L224</a>
- Start line: `171`
- End line: `224`
- Signature:

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

### Internal relationship graph

### Public related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

### Internal implementation helpers

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/governance_review__read_metadata_rows/"><code>fabricops_kit.governance_review._read_metadata_rows</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__current_database_matches/"><code>fabricops_kit.fabric_input_output._current_database_matches</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__normalize_table_name/"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></a>
- <a href="../internal/fabric_input_output__registered_table_identifier/"><code>fabricops_kit.fabric_input_output._registered_table_identifier</code></a>
- <a href="../internal/fabric_input_output__uses_registered_metadata_table/"><code>fabricops_kit.fabric_input_output._uses_registered_metadata_table</code></a>

</details>
