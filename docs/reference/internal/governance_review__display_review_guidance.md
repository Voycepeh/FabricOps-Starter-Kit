# _display_review_guidance

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../widget_review_column_classification/"><code>fabricops_kit.governance_review.widget_review_column_classification</code></a>
- <a href="../widget_review_column_context/"><code>fabricops_kit.governance_review.widget_review_column_context</code></a>
- <a href="../widget_review_dq_rules/"><code>fabricops_kit.governance_review.widget_review_dq_rules</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._display_review_guidance`
- Short name: `_display_review_guidance`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/governance_review.py#L429-L443">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 1

## Inbound references
- <a href="../widget_review_column_classification/"><code>fabricops_kit.governance_review.widget_review_column_classification</code></a>
- <a href="../widget_review_column_context/"><code>fabricops_kit.governance_review.widget_review_column_context</code></a>
- <a href="../widget_review_dq_rules/"><code>fabricops_kit.governance_review.widget_review_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
