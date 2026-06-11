# _is_table_not_found_error

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>

## Purpose

Return whether a Spark/read exception clearly means the table is absent.

## Signature if available

```python
def _is_table_not_found_error(exc: Exception) -> bool
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._is_table_not_found_error`
- Short name: `_is_table_not_found_error`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/governance_review.py#L199-L219">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
