# _build_column_context_records

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

## Purpose

Build append-only approved business-context records from explicit reviews.

## Signature if available

```python
def _build_column_context_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any=None, env: str | None=None, approved_by: str | None=None) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._build_column_context_records`
- Short name: `_build_column_context_records`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/governance_review.py#L410-L423">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 3

## Inbound references
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

## Outbound references
- <a href="../internal/governance_review__approved_column_identity/"><code>fabricops_kit.governance_review._approved_column_identity</code></a>
- <a href="../internal/governance_review__approved_review_context/"><code>fabricops_kit.governance_review._approved_review_context</code></a>
- <a href="../internal/governance_review__json/"><code>fabricops_kit.governance_review._json</code></a>
