# _audit_timestamp_expr

**Module:** `config`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>

## Purpose

Return a Spark expression for the current audit timestamp timezone.

## Signature if available

```python
def _audit_timestamp_expr(config: Any=None, timezone_name: str | None=None)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._audit_timestamp_expr`
- Short name: `_audit_timestamp_expr`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/8f8ba1a4c1e063896508520952dedc3eda348629/src/fabricops_kit/config.py#L78-L83">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>

## Outbound references
- <a href="../internal/config__get_audit_timezone/"><code>fabricops_kit.config._get_audit_timezone</code></a>
