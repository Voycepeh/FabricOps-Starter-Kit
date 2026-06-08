# _load_active_dq_rules

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__enforce_dq/"><code>fabricops_kit.governance_review._enforce_dq</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

## Purpose

Load active DQ rules from current v1 metadata rows.

## Signature if available

```python
def _load_active_dq_rules(metadata_df, table_name: str, env_name: str | None=None, dataset_name: str | None=None) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._load_active_dq_rules`
- Short name: `_load_active_dq_rules`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/governance_review.py#L706-L740">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 5

## Inbound references
- <a href="../internal/governance_review__enforce_dq/"><code>fabricops_kit.governance_review._enforce_dq</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
- <a href="../internal/governance_review__latest_dq_rule_versions/"><code>fabricops_kit.governance_review._latest_dq_rule_versions</code></a>
- <a href="../internal/governance_review__spark_sql_helpers/"><code>fabricops_kit.governance_review._spark_sql_helpers</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
