# _setup_governance_metadata_tables

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Purpose

Create or validate governance metadata tables via the configured route.

## Signature if available

```python
def _setup_governance_metadata_tables(*, spark: Any, config: Any, env: str) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._setup_governance_metadata_tables`
- Short name: `_setup_governance_metadata_tables`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/governance_review.py#L172-L206">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 6

## Inbound references
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
- <a href="../internal/governance_review__get_governance_metadata_schemas/"><code>fabricops_kit.governance_review._get_governance_metadata_schemas</code></a>
- <a href="../internal/governance_review__is_table_not_found_error/"><code>fabricops_kit.governance_review._is_table_not_found_error</code></a>
- <a href="../internal/governance_review__schema_field_names/"><code>fabricops_kit.governance_review._schema_field_names</code></a>
