# prepare_source_table_configs

Enrich source table configs and load source DataFrames for 02_pipeline.

## What this is for and when to use it

Enrich source table configs and load source DataFrames for 02_pipeline.

- Use after SOURCE_TABLES and DEFAULT_SOURCE_GUARDRAILS are defined to derive source defaults, load DataFrames, and build SOURCE_CONFIG_BY_KEY.

## When not to use it

- Do not use for one-off interactive reads where no FabricOps guardrail configuration is needed.

## Example

```python
SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_source_table_configs(SOURCE_TABLES, DEFAULT_SOURCE_GUARDRAILS, CONFIG, ENV_NAME, spark)
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
      <td data-label="Parameter"><code>source_table_configs</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">User-authored ``SOURCE_TABLES`` entries. Each entry must include ``key``, ``layer``, and ``table_name``. Optional read settings include ``read_type``/``kind``, ``relative_path``, ``schema``, ``warehouse_target``, ``warehouse_table``, ``spark_table``, or ``df``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>default_source_guardrails</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Default guardrail settings merged before each source config.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">FabricOps framework configuration from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key used for configured source routing.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used for table/file/warehouse reads.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Enriched source configs and a dictionary keyed by source key.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Reads configured source DataFrames from Lakehouse tables/files, Warehouse tables, custom Spark tables, or pre-supplied DataFrames.

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/pipeline__read_source_dataframe/"><code>fabricops_kit.pipeline._read_source_dataframe</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L176-L220">View prepare_source_table_configs on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def prepare_source_table_configs(
    source_table_configs: list[dict[str, Any]],
    default_source_guardrails: Mapping[str, Any],
    config: Any,
    env: str,
    spark_session: Any,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Enrich source table configs and load source DataFrames.

    Parameters
    ----------
    source_table_configs : list of dict
        User-authored ``SOURCE_TABLES`` entries. Each entry must include
        ``key``, ``layer``, and ``table_name``. Optional read settings include
        ``read_type``/``kind``, ``relative_path``, ``schema``,
        ``warehouse_target``, ``warehouse_table``, ``spark_table``, or ``df``.
    default_source_guardrails : mapping
        Default guardrail settings merged before each source config.
    config : Any
        FabricOps framework configuration from ``00_env_config``.
    env : str
        Environment key used for configured source routing.
    spark_session : Any
        Spark session used for table/file/warehouse reads.

    Returns
    -------
    tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
        Enriched source configs and a lookup keyed by source ``key``.
    """
    enriched_sources: list[dict[str, Any]] = []
    for source_config in source_table_configs:
        dataset_name = source_config.get("dataset_name", source_config["table_name"])
        stage = source_config.get("stage", source_config["layer"])
        watermark_value = source_config.get("watermark_value", None)
        enriched_source = {
            **default_source_guardrails,
            **source_config,
            "dataset_name": dataset_name,
            "stage": stage,
            "watermark_value": watermark_value,
        }
        enriched_source["df"] = _read_source_dataframe(enriched_source, config=config, env=env, spark_session=spark_session)
        enriched_sources.append(enriched_source)
    return enriched_sources, {source_config["key"]: source_config for source_config in enriched_sources}
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.prepare_source_table_configs`
- Short name: `prepare_source_table_configs`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `176`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Uses CONFIG and env from 00_env_config so source reads follow configured Fabric targets.
- **inputs:** source_table_configs, default_source_guardrails, config, env, and spark_session.
- **output:** Enriched source configs and a dictionary keyed by source key.
- **side_effects:** Reads configured source DataFrames from Lakehouse tables/files, Warehouse tables, custom Spark tables, or pre-supplied DataFrames.
- **failure_modes:** Not documented yet
- **verification:** Verify every source has a unique key and the derived configs are passed to run_table_guardrails before transformation.

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/pipeline__read_source_dataframe/"><code>fabricops_kit.pipeline._read_source_dataframe</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L176-L220">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L176-L220</a>
- Start line: `176`
- End line: `220`
- Signature:

```python
def prepare_source_table_configs(source_table_configs: list[dict[str, Any]], default_source_guardrails: Mapping[str, Any], config: Any, env: str, spark_session: Any) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Internal implementation helpers

- <a href="../internal/pipeline__read_source_dataframe/"><code>fabricops_kit.pipeline._read_source_dataframe</code></a>

</details>
