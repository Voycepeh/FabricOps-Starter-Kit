# _profile_watermark_bounds

**Module:** `guardrails`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _profile_watermark_bounds(profile, watermark_column: str | None) -> tuple[str, str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.guardrails._profile_watermark_bounds`
- Short name: `_profile_watermark_bounds`
- Module: `guardrails`
- Classification: Internal
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/guardrails.py#L511-L518">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>

## Outbound references
- <a href="../internal/guardrails__normalize_profile/"><code>fabricops_kit.guardrails._normalize_profile</code></a>
- <a href="../internal/guardrails__string_value/"><code>fabricops_kit.guardrails._string_value</code></a>
