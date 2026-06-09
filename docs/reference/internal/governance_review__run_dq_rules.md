# _run_dq_rules

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

## Purpose

Run DQ rules and return rule-level PASS/FAIL evidence.

## Signature if available

```python
def _run_dq_rules(df, table_name: str, rules: list[dict[str, Any]])
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._run_dq_rules`
- Short name: `_run_dq_rules`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d7fae51cae8b101fbee48f365b462f6b6f647e79/src/fabricops_kit/governance_review.py#L1222-L1233">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 3

## Inbound references
- <a href="../internal/governance_review__enforce_dq/"><code>fabricops_kit.governance_review._enforce_dq</code></a>

## Outbound references
- <a href="../internal/governance_review__spark_sql_helpers/"><code>fabricops_kit.governance_review._spark_sql_helpers</code></a>
- <a href="../internal/governance_review__split_dq_rows/"><code>fabricops_kit.governance_review._split_dq_rows</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
