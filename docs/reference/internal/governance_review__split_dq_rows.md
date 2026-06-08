# _split_dq_rows

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
- <a href="../internal/governance_review__run_dq_rules/"><code>fabricops_kit.governance_review._run_dq_rules</code></a>

## Purpose

Split source rows into valid rows, quarantine rows, and failure evidence.

## Signature if available

```python
def _split_dq_rows(df, rules: list[dict[str, Any]], dq_run_id: str | None=None, row_id_columns: list[str] | None=None)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._split_dq_rows`
- Short name: `_split_dq_rows`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/governance_review.py#L945-L992">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../internal/governance_review__enforce_dq/"><code>fabricops_kit.governance_review._enforce_dq</code></a>
- <a href="../internal/governance_review__run_dq_rules/"><code>fabricops_kit.governance_review._run_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__spark_sql_helpers/"><code>fabricops_kit.governance_review._spark_sql_helpers</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
