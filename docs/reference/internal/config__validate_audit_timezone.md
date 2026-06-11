# _validate_audit_timezone

**Module:** `config`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/config__get_audit_timezone/"><code>fabricops_kit.config._get_audit_timezone</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>

## Purpose

Return a valid IANA audit timezone name.

## Signature if available

```python
def _validate_audit_timezone(timezone_name: str | None) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._validate_audit_timezone`
- Short name: `_validate_audit_timezone`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/8f8ba1a4c1e063896508520952dedc3eda348629/src/fabricops_kit/config.py#L27-L58">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 0

## Inbound references
- <a href="../internal/config__get_audit_timezone/"><code>fabricops_kit.config._get_audit_timezone</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
