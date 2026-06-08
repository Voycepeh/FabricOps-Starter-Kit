# _approved_column_identity

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _approved_column_identity(profile_row: dict[str, Any], review_row: dict[str, Any], *, env: str | None=None) -> dict[str, str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._approved_column_identity`
- Short name: `_approved_column_identity`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/governance_review.py#L76-L88">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 3

## Inbound references
- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

## Outbound references
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
- <a href="../internal/metadata__build_metadata_column_key/"><code>fabricops_kit.metadata._build_metadata_column_key</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
