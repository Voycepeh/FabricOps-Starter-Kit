# SchemaDriftError

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

## Purpose

Raised when a schema check is configured to fail on drift.

## Signature if available

```python
class SchemaDriftError(Exception)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift.SchemaDriftError`
- Short name: `SchemaDriftError`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d7fae51cae8b101fbee48f365b462f6b6f647e79/src/fabricops_kit/drift.py#L18-L25">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>
