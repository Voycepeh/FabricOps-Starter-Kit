# _actual_schema

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/drift__schema_hash_from_dataframe/"><code>fabricops_kit.drift._schema_hash_from_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _actual_schema(df) -> tuple[list[str], dict[str, str]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._actual_schema`
- Short name: `_actual_schema`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ffb9386812c13cf40a6a40503d36bd7a16dc5e31/src/fabricops_kit/drift.py#L87-L102">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 1

## Inbound references
- <a href="../internal/drift__schema_hash_from_dataframe/"><code>fabricops_kit.drift._schema_hash_from_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>

## Outbound references
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>
