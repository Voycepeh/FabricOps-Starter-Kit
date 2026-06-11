# _build_lineage_records

**Module:** `data_lineage`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

Not documented yet

## Purpose

Build metadata-ready lineage rows from validated lineage steps.

## Signature if available

```python
def _build_lineage_records(dataset_name: str, lineage_steps: list[dict], run_id: str | None=None, notebook_name: str | None=None, workspace_name: str | None=None, workspace_id: str | None=None, notebook_id: str | None=None, created_by: str | None=None, config: Any=None) -> list[dict]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_lineage._build_lineage_records`
- Short name: `_build_lineage_records`
- Module: `data_lineage`
- Classification: Internal
- Related module: `data_lineage`
- Source file path: `src/fabricops_kit/data_lineage.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/data_lineage.py#L166-L209">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 2

## Outbound references
- <a href="../internal/config__current_audit_timestamp/"><code>fabricops_kit.config._current_audit_timestamp</code></a>
- <a href="../internal/data_lineage__validate_lineage_steps/"><code>fabricops_kit.data_lineage._validate_lineage_steps</code></a>
