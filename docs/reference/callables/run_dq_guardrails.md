# run_dq_guardrails

Run approved DQ guardrails for many datasets using per-dataset presets.

## What this is for and when to use it

Run approved DQ guardrails for many datasets using per-dataset presets.

- Use for source and target DQ checks where each definition supplies dq_preset.

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
      <td data-label="Meaning">Definitions containing dataset/table identity and optional ``dq_preset``. Use ``&quot;skip&quot;`` to explicitly skip DQ for a dataset.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">``00_env_config`` route configuration used to read ``METADATA_DQ_RULES``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key from ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Spark session passed to metadata read helpers.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of DQ guardrail results keyed by dataset alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L251-L294">View run_dq_guardrails on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def run_dq_guardrails(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    spark_session: Any = None,
) -> dict[str, dict[str, Any]]:
    """Run approved DQ guardrails for many datasets with per-dataset presets.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Source or target DataFrames keyed by alias.
    dataset_definitions : mapping of str to mapping
        Definitions containing dataset/table identity and optional ``dq_preset``.
        Use ``"skip"`` to explicitly skip DQ for a dataset.
    config : FrameworkConfig or dict
        ``00_env_config`` route configuration used to read ``METADATA_DQ_RULES``.
    env : str
        Environment key from ``00_env_config``.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session passed to metadata read helpers.

    Returns
    -------
    dict[str, dict]
        DQ guardrail results keyed by dataset alias.
    """
    results: dict[str, dict[str, Any]] = {}
    for name, dataframe in datasets.items():
        definition = dataset_definitions[name]
        if str(definition.get("dq_preset", "approved_rules")).lower() in {"skip", "none", "off"}:
            results[name] = {"status": "skipped", "can_continue": True, "checks": [], "message": "DQ guardrail skipped by preset."}
            continue
        results[name] = enforce_dq_rules(
            dataframe,
            config,
            env,
            str(definition.get("dataset_name") or _definition_name(name, definition)),
            _definition_name(name, definition),
            spark_session=spark_session,
        )
    return results
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_dq_guardrails`
- Short name: `run_dq_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `251`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `DQ guardrails`.
- **inputs:** datasets, dataset_definitions, config, env, and optional spark_session.
- **output:** Dictionary of DQ guardrail results keyed by dataset alias.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L251-L294">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L251-L294</a>
- Start line: `251`
- End line: `294`
- Signature:

```python
def run_dq_guardrails(datasets: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, config: Any, env: str, spark_session: Any=None) -> dict[str, dict[str, Any]]
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>
