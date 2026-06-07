# _spark_types

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__get_governance_metadata_schemas/"><code>fabricops_kit.governance_review._get_governance_metadata_schemas</code></a>
- <a href="../internal/governance_review__schema/"><code>fabricops_kit.governance_review._schema</code></a>

## Purpose

Return Spark SQL type classes lazily so package import stays lightweight.

## Signature if available

```python
def _spark_types()
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._spark_types`
- Short name: `_spark_types`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4c16c62a2fd27c5a88a51c78e285c4b6e922580a/src/fabricops_kit/governance_review.py#L88-L94">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 0

## Inbound references
- <a href="../internal/governance_review__get_governance_metadata_schemas/"><code>fabricops_kit.governance_review._get_governance_metadata_schemas</code></a>
- <a href="../internal/governance_review__schema/"><code>fabricops_kit.governance_review._schema</code></a>
