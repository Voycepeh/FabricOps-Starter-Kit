# _schema_guardrail_type

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

## Purpose

Return a user-facing schema guardrail type for Spark or pandas dtypes.

## Signature if available

```python
def _schema_guardrail_type(data_type) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._schema_guardrail_type`
- Short name: `_schema_guardrail_type`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6e744d11e5f3081af2c7f10e6b37ccaaba97dd6d/src/fabricops_kit/drift.py#L95-L105">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../internal/drift__schema_profile_rows/"><code>fabricops_kit.drift._schema_profile_rows</code></a>

## Outbound references
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>
