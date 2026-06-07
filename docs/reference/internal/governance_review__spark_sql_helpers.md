# _spark_sql_helpers

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__dq_failed_expression/"><code>fabricops_kit.governance_review._dq_failed_expression</code></a>
- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__latest_dq_rule_versions/"><code>fabricops_kit.governance_review._latest_dq_rule_versions</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__run_dq_rules/"><code>fabricops_kit.governance_review._run_dq_rules</code></a>
- <a href="../internal/governance_review__split_dq_rows/"><code>fabricops_kit.governance_review._split_dq_rows</code></a>

## Purpose

Return Spark SQL helper modules lazily for DQ runtime helpers.

## Signature if available

```python
def _spark_sql_helpers()
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._spark_sql_helpers`
- Short name: `_spark_sql_helpers`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b6a5693130e525f919566c2115ac67da9c6faef/src/fabricops_kit/governance_review.py#L592-L599">View source on GitHub</a>
- Inbound references count: 9
- Outbound references count: 0

## Inbound references
- <a href="../internal/governance_review__dq_failed_expression/"><code>fabricops_kit.governance_review._dq_failed_expression</code></a>
- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__latest_dq_rule_versions/"><code>fabricops_kit.governance_review._latest_dq_rule_versions</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__run_dq_rules/"><code>fabricops_kit.governance_review._run_dq_rules</code></a>
- <a href="../internal/governance_review__split_dq_rows/"><code>fabricops_kit.governance_review._split_dq_rows</code></a>
