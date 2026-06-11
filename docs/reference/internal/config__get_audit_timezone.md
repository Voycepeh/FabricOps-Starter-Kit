# _get_audit_timezone

**Module:** `config`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/config__audit_timestamp_expr/"><code>fabricops_kit.config._audit_timestamp_expr</code></a>
- <a href="../internal/config__current_audit_timestamp/"><code>fabricops_kit.config._current_audit_timestamp</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Purpose

Resolve the configured FabricOps audit timezone, defaulting to UTC.

## Signature if available

```python
def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._get_audit_timezone`
- Short name: `_get_audit_timezone`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/config.py#L61-L66">View source on GitHub</a>
- Inbound references count: 4
- Outbound references count: 1

## Inbound references
- <a href="../internal/config__audit_timestamp_expr/"><code>fabricops_kit.config._audit_timestamp_expr</code></a>
- <a href="../internal/config__current_audit_timestamp/"><code>fabricops_kit.config._current_audit_timestamp</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Outbound references
- <a href="../internal/config__validate_audit_timezone/"><code>fabricops_kit.config._validate_audit_timezone</code></a>
