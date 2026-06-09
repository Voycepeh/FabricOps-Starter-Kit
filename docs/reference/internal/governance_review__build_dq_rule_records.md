# _build_dq_rule_records

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

Build append-only approved DQ-rule records without enforcing them.

## Signature if available

```python
def _build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any=None, env: str | None=None, approved_by: str | None=None) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._build_dq_rule_records`
- Short name: `_build_dq_rule_records`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/governance_review.py#L413-L432">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 5

## Inbound references
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

## Outbound references
- <a href="../internal/governance_review__approved_column_identity/"><code>fabricops_kit.governance_review._approved_column_identity</code></a>
- <a href="../internal/governance_review__approved_review_context/"><code>fabricops_kit.governance_review._approved_review_context</code></a>
- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
- <a href="../internal/governance_review__json/"><code>fabricops_kit.governance_review._json</code></a>
- <a href="../internal/metadata__build_dq_rule_key/"><code>fabricops_kit.metadata._build_dq_rule_key</code></a>
