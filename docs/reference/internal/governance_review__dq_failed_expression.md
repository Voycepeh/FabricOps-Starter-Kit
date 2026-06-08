# _dq_failed_expression

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>

## Purpose

Build a Spark boolean expression identifying rows that fail one DQ rule.

## Signature if available

```python
def _dq_failed_expression(df, rule: dict[str, Any])
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._dq_failed_expression`
- Short name: `_dq_failed_expression`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/governance_review.py#L741-L767">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 1

## Inbound references
- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>

## Outbound references
- <a href="../internal/governance_review__spark_sql_helpers/"><code>fabricops_kit.governance_review._spark_sql_helpers</code></a>
