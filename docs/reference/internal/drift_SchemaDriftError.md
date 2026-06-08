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
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/drift.py#L16-L23">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>
