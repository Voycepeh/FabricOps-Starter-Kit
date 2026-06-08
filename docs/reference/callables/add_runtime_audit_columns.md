# add_runtime_audit_columns

Add standard FabricOps runtime audit columns to target DataFrames.

## What this is for and when to use it

Add standard FabricOps runtime audit columns to target DataFrames.

- Use after defining target DataFrames and before target schema, drift, DQ, and write steps.

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
      <td data-label="Meaning">Target DataFrames keyed by alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pipeline run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>pipeline_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Pipeline name stamped onto each row.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>created_at</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Deterministic timestamp override. Defaults to current UTC time.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of audited DataFrames keyed by target alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

- <a href="../write_pipeline_targets/"><code>fabricops_kit.pipeline.write_pipeline_targets</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L408-L442">View add_runtime_audit_columns on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def add_runtime_audit_columns(
    datasets: Mapping[str, Any],
    *,
    run_id: str,
    pipeline_name: str = "",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Add standard runtime audit columns to many target DataFrames.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        Target DataFrames keyed by alias.
    run_id : str
        Pipeline run identifier.
    pipeline_name : str, optional
        Pipeline name stamped onto each row.
    created_at : str, optional
        Deterministic timestamp override. Defaults to current UTC time.

    Returns
    -------
    dict[str, DataFrame]
        DataFrames with ``_fabricops_run_id``, ``_fabricops_pipeline_name``, and
        ``_fabricops_created_at`` columns added.
    """
    from pyspark.sql import functions as F

    timestamp = created_at or _now_iso()
    return {
        name: dataframe.withColumn("_fabricops_run_id", F.lit(run_id))
        .withColumn("_fabricops_pipeline_name", F.lit(pipeline_name))
        .withColumn("_fabricops_created_at", F.lit(timestamp))
        for name, dataframe in datasets.items()
    }
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.add_runtime_audit_columns`
- Short name: `add_runtime_audit_columns`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `408`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Target definitions`.
- **inputs:** datasets, run_id, pipeline_name, and optional created_at.
- **output:** Dictionary of audited DataFrames keyed by target alias.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L408-L442">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L408-L442</a>
- Start line: `408`
- End line: `442`
- Signature:

```python
def add_runtime_audit_columns(datasets: Mapping[str, Any], *, run_id: str, pipeline_name: str='', created_at: str | None=None) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../write_pipeline_targets/"><code>fabricops_kit.pipeline.write_pipeline_targets</code></a>

### Internal implementation helpers

- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>

</details>
