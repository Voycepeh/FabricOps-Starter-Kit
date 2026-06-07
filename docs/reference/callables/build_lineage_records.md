# build_lineage_records

**Module:** `data_lineage`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use in pipeline notebooks to build source-to-target lineage evidence rows for a completed transformation run.

## When not to use this

Do not use to scan notebooks automatically or persist metadata; it only builds records from supplied lineage inputs.

## Quick example

lineage_rows = build_lineage_records(dataset_name=dataset_name, run_id=run_id, source_tables=["source.orders"], target_table="unified.orders", transformation_steps=[{"step": "clean_orders"}])

## Signature

```python
def build_lineage_records(*, dataset_name: str, run_id: str, source_tables: list[str], target_table: str, transformation_steps: list[dict]) -> list[dict]
```

## Parameters

dataset_name, run_id, source_tables, target_table, and transformation_steps.

## Returns

List of lineage record dictionaries suitable for metadata persistence.

## Raises

Raises normal Python errors if required lineage inputs are missing or malformed.

## Side effects

Pure record-building helper; it does not write metadata, tables, or files.

## FabricOps context

Use with run context from 00_env_config and persist through configured metadata routing when lineage evidence is required.

## AI implementation contract

- **required_context:** Use with run context from 00_env_config and persist through configured metadata routing when lineage evidence is required.
- **inputs:** dataset_name, run_id, source_tables, target_table, and transformation_steps.
- **output:** List of lineage record dictionaries suitable for metadata persistence.
- **side_effects:** Pure record-building helper; it does not write metadata, tables, or files.
- **failure_modes:** Raises normal Python errors if required lineage inputs are missing or malformed.
- **verification:** Verify each source table, target table, transformation step, dataset_name, and run_id are populated before persisting lineage records.

## Related functions

- <a href="../setup_notebook/"><code>fabricops_kit.config.setup_notebook</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/data_lineage.py`
- Source reference: <a href="../../api/modules/data_lineage/#build_lineage_records">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.data_lineage.build_lineage_records`
- Short name: `build_lineage_records`
- Module: `data_lineage`
- Classification: Callable
- Related module: `data_lineage`
- Inbound references count: 0
- Outbound references count: 0

_No inbound or outbound references detected._
