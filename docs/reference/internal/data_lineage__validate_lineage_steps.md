# _validate_lineage_steps

**Module:** `data_lineage`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_lineage__build_lineage_records/"><code>fabricops_kit.data_lineage._build_lineage_records</code></a>

## Purpose

Validate lineage step structure and flag records requiring human review.

## Signature if available

```python
def _validate_lineage_steps(lineage_steps: Any) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_lineage._validate_lineage_steps`
- Short name: `_validate_lineage_steps`
- Module: `data_lineage`
- Classification: Internal
- Related module: `data_lineage`
- Source file path: `src/fabricops_kit/data_lineage.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ffb9386812c13cf40a6a40503d36bd7a16dc5e31/src/fabricops_kit/data_lineage.py#L129-L162">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/data_lineage__build_lineage_records/"><code>fabricops_kit.data_lineage._build_lineage_records</code></a>
