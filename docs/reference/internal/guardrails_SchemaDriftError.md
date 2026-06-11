# SchemaDriftError

**Module:** `guardrails`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

## Purpose

Raised when a guardrail check is configured to stop execution.

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

- Fully qualified function name: `fabricops_kit.guardrails.SchemaDriftError`
- Short name: `SchemaDriftError`
- Module: `guardrails`
- Classification: Internal
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/guardrails.py#L27-L34">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>
