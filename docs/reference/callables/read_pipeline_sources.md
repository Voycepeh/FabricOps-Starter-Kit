# read_pipeline_sources

Read many pipeline source definitions into DataFrames.

## What this is for and when to use it

Read many pipeline source definitions into DataFrames.

- Use in 02_pipeline after defining SOURCE_DEFINITIONS for one or more lakehouse, warehouse, or file sources.

## When not to use it

- Not documented yet

## Example

```python
Not documented yet
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
      <td data-label="Parameter"><code>source_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source definitions keyed by dataset alias. Each definition must include ``kind`` and routing fields. Supported ``kind`` values are ``lakehouse``, ``warehouse``, ``csv``, ``parquet``, and ``excel``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">``00_env_config`` configuration used for routed reads.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark session to pass to read helpers.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of DataFrames keyed by source alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Reads source data through the configured Fabric routes.

## Related functions

- <a href="../profile_pipeline_datasets/"><code>fabricops_kit.pipeline.profile_pipeline_datasets</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L80-L130">View read_pipeline_sources on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def read_pipeline_sources(
    source_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    spark_session: Any = None,
) -> dict[str, Any]:
    """Read many source datasets from notebook-friendly source definitions.

    Parameters
    ----------
    source_definitions : mapping of str to mapping
        Source definitions keyed by dataset alias. Each definition must include
        ``kind`` and routing fields. Supported ``kind`` values are
        ``lakehouse``, ``warehouse``, ``csv``, ``parquet``, and ``excel``.
    config : FrameworkConfig or dict
        ``00_env_config`` configuration used for routed reads.
    env : str
        Environment key from ``00_env_config``.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session to pass to read helpers.

    Returns
    -------
    dict[str, pyspark.sql.DataFrame]
        DataFrames keyed by the same aliases as ``source_definitions``.

    Notes
    -----
    This helper keeps read plumbing out of ``02_pipeline`` while preserving
    metadata lakehouse routing from ``00_env_config``.
    """
    dataframes: dict[str, Any] = {}
    for name, definition in source_definitions.items():
        kind = str(definition.get("kind", "lakehouse")).lower()
        layer = str(definition.get("layer") or definition.get("target") or "source")
        table = _definition_name(name, definition)
        if kind == "lakehouse":
            dataframes[name] = read_lakehouse_table(config, env, layer, table, spark_session=spark_session)
        elif kind == "warehouse":
            schema = str(definition.get("schema", "dbo"))
            dataframes[name] = read_warehouse_table(config, env, layer, schema, table, spark_session=spark_session)
        elif kind == "csv":
            dataframes[name] = read_lakehouse_csv(config, env, layer, str(definition["path"]), spark_session=spark_session, header=bool(definition.get("header", True)))
        elif kind == "parquet":
            dataframes[name] = read_lakehouse_parquet(config, env, layer, str(definition["path"]), spark_session=spark_session)
        elif kind == "excel":
            dataframes[name] = read_lakehouse_excel(config, env, layer, str(definition["path"]), spark_session=spark_session)
        else:
            raise ValueError(f"Unsupported source kind for {name!r}: {kind!r}.")
    return dataframes
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.read_pipeline_sources`
- Short name: `read_pipeline_sources`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `80`
- Inbound references count: 0
- Outbound references count: 6

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Source reads`.
- **inputs:** source_definitions plus config, env, and optional spark_session.
- **output:** Dictionary of DataFrames keyed by source alias.
- **side_effects:** Reads source data through the configured Fabric routes.
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L80-L130">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L80-L130</a>
- Start line: `80`
- End line: `130`
- Signature:

```python
def read_pipeline_sources(source_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, spark_session: Any=None) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../profile_pipeline_datasets/"><code>fabricops_kit.pipeline.profile_pipeline_datasets</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation helpers

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>
