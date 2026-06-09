# _enforce_dq

**Module:** `governance_review`  
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

Enforce approved DQ rules and return structured deterministic outputs.

## Signature if available

```python
def _enforce_dq(df, *, table_name: str, rules=None, metadata_df=None, row_id_columns: list[str] | None=None, dq_run_id: str | None=None) -> DQEnforcementResult
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._enforce_dq`
- Short name: `_enforce_dq`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/governance_review.py#L1272-L1280">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 5

## Outbound references
- <a href="../internal/governance_review_DQEnforcementResult/"><code>fabricops_kit.governance_review.DQEnforcementResult</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__run_dq_rules/"><code>fabricops_kit.governance_review._run_dq_rules</code></a>
- <a href="../internal/governance_review__split_dq_rows/"><code>fabricops_kit.governance_review._split_dq_rows</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
