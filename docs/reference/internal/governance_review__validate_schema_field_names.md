# _validate_schema_field_names

**Module:** `governance_review`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__schema/"><code>fabricops_kit.governance_review._schema</code></a>

## Purpose

Validate that a metadata schema has no case-insensitive duplicates.

## Signature if available

```python
def _validate_schema_field_names(table_name: str, fields: list[tuple[str, Any]]) -> None
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._validate_schema_field_names`
- Short name: `_validate_schema_field_names`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/governance_review.py#L112-L137">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/governance_review__schema/"><code>fabricops_kit.governance_review._schema</code></a>
