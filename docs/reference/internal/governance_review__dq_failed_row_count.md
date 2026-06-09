# _dq_failed_row_count

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

## Purpose

Return the count of rows that failed at least one DQ rule.

## Signature if available

```python
def _dq_failed_row_count(df, rules: list[dict[str, Any]]) -> int
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._dq_failed_row_count`
- Short name: `_dq_failed_row_count`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/governance_review.py#L1062-L1072">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__dq_failed_expression/"><code>fabricops_kit.governance_review._dq_failed_expression</code></a>
- <a href="../internal/governance_review__spark_sql_helpers/"><code>fabricops_kit.governance_review._spark_sql_helpers</code></a>
