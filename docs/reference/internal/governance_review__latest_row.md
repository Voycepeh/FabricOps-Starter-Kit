# _latest_row

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../review_pipeline_run/"><code>fabricops_kit.governance_review.review_pipeline_run</code></a>

## Purpose

Return the latest row by non-empty string sort fields.

## Signature if available

```python
def _latest_row(rows: list[dict[str, Any]], *sort_fields: str) -> dict[str, Any] | None
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._latest_row`
- Short name: `_latest_row`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#_latest_row">Module source anchor</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../review_pipeline_run/"><code>fabricops_kit.governance_review.review_pipeline_run</code></a>

## Outbound references
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
