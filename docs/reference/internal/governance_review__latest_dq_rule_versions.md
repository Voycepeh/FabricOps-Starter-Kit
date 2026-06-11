# _latest_dq_rule_versions

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>

## Purpose

Resolve latest append-only DQ metadata rows by stable rule identity.

## Signature if available

```python
def _latest_dq_rule_versions(metadata_df, table_name: str, env_name: str | None=None, dataset_name: str | None=None)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._latest_dq_rule_versions`
- Short name: `_latest_dq_rule_versions`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/governance_review.py#L1259-L1280">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__spark_sql_helpers/"><code>fabricops_kit.governance_review._spark_sql_helpers</code></a>
