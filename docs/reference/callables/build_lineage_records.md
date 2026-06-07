# build_lineage_records

**Module:** `data_lineage`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Build source-to-target lineage evidence records for a pipeline run.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def build_lineage_records(*, dataset_name: str, run_id: str, source_tables: list[str], target_table: str, transformation_steps: list[dict]) -> list[dict]
```

## Parameters

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

## Returns

list of dict
    Row dictionaries suitable for metadata persistence.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline`; segment: `Lineage evidence`.

## AI implementation contract

Not documented yet

## Related functions

Not documented yet

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
