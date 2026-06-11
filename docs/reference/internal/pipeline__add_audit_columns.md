# _add_audit_columns

**Module:** `pipeline`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../prepare_pipeline_table_configs/"><code>fabricops_kit.pipeline.prepare_pipeline_table_configs</code></a>

## Purpose

Return a DataFrame with standard FabricOps target audit columns.

## Signature if available

```python
def _add_audit_columns(dataframe: Any, *, run_id: str, pipeline_name: str)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.pipeline._add_audit_columns`
- Short name: `_add_audit_columns`
- Module: `pipeline`
- Classification: Internal
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/pipeline.py#L113-L123">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../prepare_pipeline_table_configs/"><code>fabricops_kit.pipeline.prepare_pipeline_table_configs</code></a>
