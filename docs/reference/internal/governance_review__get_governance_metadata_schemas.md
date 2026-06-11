# _get_governance_metadata_schemas

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/config__get_active_metadata_tables/"><code>fabricops_kit.config._get_active_metadata_tables</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>

## Purpose

Return typed Spark schemas prepared by ``00_env_config`` for governance.

## Signature if available

```python
def _get_governance_metadata_schemas() -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._get_governance_metadata_schemas`
- Short name: `_get_governance_metadata_schemas`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/8f8ba1a4c1e063896508520952dedc3eda348629/src/fabricops_kit/governance_review.py#L152-L195">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../internal/config__get_active_metadata_tables/"><code>fabricops_kit.config._get_active_metadata_tables</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>

## Outbound references
- <a href="../internal/governance_review__schema/"><code>fabricops_kit.governance_review._schema</code></a>
- <a href="../internal/governance_review__spark_types/"><code>fabricops_kit.governance_review._spark_types</code></a>
