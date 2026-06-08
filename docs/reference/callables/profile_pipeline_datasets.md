# profile_pipeline_datasets

Profile many source or target datasets from definitions.

## What this is for and when to use it

Profile many source or target datasets from definitions.

- Use after reading sources or defining targets so profiles can feed drift and catalogue evidence.

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
      <td data-label="Meaning">DataFrames keyed by source or target alias.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_definitions</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Dataset definitions containing table names and optional profiling options such as ``exclude_columns`` and ``distribution_columns``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>include_distributions</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Whether to capture lightweight distribution evidence for drift checks.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Dictionary of profile DataFrames keyed by dataset alias.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/pipeline.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L133-L166">View profile_pipeline_datasets on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def profile_pipeline_datasets(
    datasets: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    include_distributions: bool = True,
) -> dict[str, Any]:
    """Profile many source or target DataFrames using their definitions.

    Parameters
    ----------
    datasets : mapping of str to DataFrame
        DataFrames keyed by source or target alias.
    dataset_definitions : mapping of str to mapping
        Dataset definitions containing table names and optional profiling
        options such as ``exclude_columns`` and ``distribution_columns``.
    include_distributions : bool, default=True
        Whether to capture lightweight distribution evidence for drift checks.

    Returns
    -------
    dict[str, DataFrame]
        Profile DataFrames keyed by dataset alias.
    """
    profiles: dict[str, Any] = {}
    for name, dataframe in datasets.items():
        definition = dataset_definitions[name]
        profiles[name] = profile_dataframe(
            dataframe,
            table_name=_definition_name(name, definition),
            exclude_columns=definition.get("exclude_columns"),
            include_distributions=bool(definition.get("include_distributions", include_distributions)),
            distribution_columns=definition.get("distribution_columns"),
        )
    return profiles
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.profile_pipeline_datasets`
- Short name: `profile_pipeline_datasets`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `133`
- Inbound references count: 0
- Outbound references count: 2

### AI implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Profiling`.
- **inputs:** datasets, dataset_definitions, and include_distributions.
- **output:** Dictionary of profile DataFrames keyed by dataset alias.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L133-L166">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/pipeline.py#L133-L166</a>
- Start line: `133`
- End line: `166`
- Signature:

```python
def profile_pipeline_datasets(datasets: Mapping[str, Any], dataset_definitions: Mapping[str, Mapping[str, Any]], *, include_distributions: bool=True) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Internal implementation helpers

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/pipeline__definition_name/"><code>fabricops_kit.pipeline._definition_name</code></a>

</details>
