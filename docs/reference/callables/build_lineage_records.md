# build_lineage_records

Build source-to-target lineage evidence records for a pipeline run.

## Use this when

Use in pipeline notebooks to build source-to-target lineage evidence rows for a completed transformation run.

## Do not use this for

Do not use to scan notebooks automatically or persist metadata; it only builds records from supplied lineage inputs.

## Example

```python
lineage_rows = build_lineage_records(dataset_name=dataset_name, run_id=run_id, source_tables=["source.orders"], target_table="unified.orders", transformation_steps=[{"step": "clean_orders"}])
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>What it means</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Dataset identifier for all output rows.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Unique run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>source_tables</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Source table names captured for the run.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>target_table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Target table name produced by the run.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>transformation_steps</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Transformation step dictionaries to merge into each output row.</td>
    </tr>
  </tbody>
</table>
</div>

<details class="reference-signature-details">
<summary>Full signature</summary>

```python
def build_lineage_records(*, dataset_name: str, run_id: str, source_tables: list[str], target_table: str, transformation_steps: list[dict]) -> list[dict]
```

</details>

## Output

List of lineage record dictionaries suitable for metadata persistence.

## Raises

Raises normal Python errors if required lineage inputs are missing or malformed.

## Side effects

Pure record-building helper; it does not write metadata, tables, or files.

## Related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

<details class="reference-metadata-details">
<summary>AI implementation contract</summary>

These fields are generated for agents and maintainers, not for quick-start reading.

- **required_context:** Use with run context from 00_env_config and persist through configured metadata routing when lineage evidence is required.
- **inputs:** dataset_name, run_id, source_tables, target_table, and transformation_steps.
- **output:** List of lineage record dictionaries suitable for metadata persistence.
- **side_effects:** Pure record-building helper; it does not write metadata, tables, or files.
- **failure_modes:** Raises normal Python errors if required lineage inputs are missing or malformed.
- **verification:** Verify each source table, target table, transformation step, dataset_name, and run_id are populated before persisting lineage records.

</details>

<details class="reference-metadata-details">
<summary>Function manifest</summary>

- Fully qualified function name: `fabricops_kit.data_lineage.build_lineage_records`
- Short name: `build_lineage_records`
- Module: `data_lineage`
- Classification: Callable
- Related module: `data_lineage`
- Source file path: `src/fabricops_kit/data_lineage.py`
- Source line: `209`
- Inbound references count: 0
- Outbound references count: 0

</details>

<details class="reference-metadata-details">
<summary>Raw inbound and outbound references</summary>

### Inbound references

Not documented yet

### Outbound references

Not documented yet

</details>

## Source code

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b6a5693130e525f919566c2115ac67da9c6faef/src/fabricops_kit/data_lineage.py#L209-L230">View build_lineage_records on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def build_lineage_records(*, dataset_name: str, run_id: str, source_tables: list[str], target_table: str, transformation_steps: list[dict]) -> list[dict]:
    """Build compact lineage records for downstream metadata sinks.

    Parameters
    ----------
    dataset_name : str
        Dataset identifier for all output rows.
    run_id : str
        Unique run identifier.
    source_tables : list of str
        Source table names captured for the run.
    target_table : str
        Target table name produced by the run.
    transformation_steps : list of dict
        Transformation step dictionaries to merge into each output row.

    Returns
    -------
    list of dict
        Row dictionaries suitable for metadata persistence.
    """
    return [{"run_id": run_id, "dataset_name": dataset_name, "source_tables": source_tables, "target_table": target_table, **s} for s in transformation_steps]
```

</details>
