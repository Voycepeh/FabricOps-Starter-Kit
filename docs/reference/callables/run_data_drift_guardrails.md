# run_data_drift_guardrails

Run data drift guardrails for many datasets using per-dataset presets.

## What this is for and when to use it

Run data drift guardrails for many datasets using per-dataset presets.

- Use for source and target drift checks where each definition supplies stage and drift_preset.

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
      <td data-label="Parameter"><code>datasets</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source or target DataFrames keyed by alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Definitions containing dataset/table identity, ``stage``, and optional ``drift_preset`` values.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used by drift helpers to read catalogue evidence.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">``00_env_config`` route configuration.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Catalogue metadata table used for baseline lookup.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Current run id excluded from baseline lookup.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of drift guardrail results keyed by dataset alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L198-L248">View run_data_drift_guardrails on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def run_data_drift_guardrails(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    spark: Any,
    config: Any,
    env: str,
    metadata_table: str = CATALOGUE_TABLE,
    run_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Run data drift guardrails for many datasets with per-dataset presets.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Source or target DataFrames keyed by alias.
    dataset_definitions : mapping of str to mapping
        Definitions containing dataset/table identity, ``stage``, and optional
        ``drift_preset`` values.
    spark : pyspark.sql.SparkSession
        Spark session used by drift helpers to read catalogue evidence.
    config : FrameworkConfig or dict
        ``00_env_config`` route configuration.
    env : str
        Environment key from ``00_env_config``.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
        Catalogue metadata table used for baseline lookup.
    run_id : str, optional
        Current run id excluded from baseline lookup.

    Returns
    -------
    dict[str, dict]
        Drift guardrail results keyed by dataset alias.
    """
    results: dict[str, dict[str, Any]] = {}
    for name, dataframe in datasets.items():
        definition = dataset_definitions[name]
        results[name] = monitor_data_changes(
            spark,
            dataframe,
            metadata_table,
            str(definition.get("dataset_name") or _definition_name(name, definition)),
            _definition_name(name, definition),
            stage=str(definition.get("stage", "target")),
            preset=str(definition.get("drift_preset", "changing_data")),
            exclude_run_id=run_id,
            distribution_columns=definition.get("distribution_columns"),
            policy_overrides=definition.get("drift_policy_overrides"),
        )
    return results
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_data_drift_guardrails`
- Short name: `run_data_drift_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `198`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Data drift guardrails`.
- **inputs:** datasets, dataset_definitions, spark, config, env, metadata_table, and optional run_id.
- **output:** Dictionary of drift guardrail results keyed by dataset alias.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L198-L248">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L198-L248</a>
- Start line: `198`
- End line: `248`
- Signature:

```python
def run_data_drift_guardrails(datasets: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, spark: Any, config: Any, env: str, metadata_table: str=CATALOGUE_TABLE, run_id: str | None=None) -> dict[str, dict[str, Any]]
```

### Internal relationship graph

### Public related functions

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Internal implementation helpers

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>
