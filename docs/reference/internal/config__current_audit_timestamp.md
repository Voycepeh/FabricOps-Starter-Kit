# _current_audit_timestamp

**Module:** `config`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_lineage__build_lineage_records/"><code>fabricops_kit.data_lineage._build_lineage_records</code></a>
- <a href="../build_lineage_records/"><code>fabricops_kit.data_lineage.build_lineage_records</code></a>
- <a href="../internal/governance_review__dq_summary/"><code>fabricops_kit.governance_review._dq_summary</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/metadata__now_utc_iso/"><code>fabricops_kit.metadata._now_utc_iso</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/pipeline__add_audit_columns/"><code>fabricops_kit.pipeline._add_audit_columns</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>

## Purpose

Return the current audit timestamp in the configured audit timezone.

## Signature if available

```python
def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._current_audit_timestamp`
- Short name: `_current_audit_timestamp`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/8f8ba1a4c1e063896508520952dedc3eda348629/src/fabricops_kit/config.py#L69-L75">View source on GitHub</a>
- Inbound references count: 9
- Outbound references count: 1

## Inbound references
- <a href="../internal/data_lineage__build_lineage_records/"><code>fabricops_kit.data_lineage._build_lineage_records</code></a>
- <a href="../build_lineage_records/"><code>fabricops_kit.data_lineage.build_lineage_records</code></a>
- <a href="../internal/governance_review__dq_summary/"><code>fabricops_kit.governance_review._dq_summary</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/metadata__now_utc_iso/"><code>fabricops_kit.metadata._now_utc_iso</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/pipeline__add_audit_columns/"><code>fabricops_kit.pipeline._add_audit_columns</code></a>
- <a href="../internal/pipeline__now_iso/"><code>fabricops_kit.pipeline._now_iso</code></a>

## Outbound references
- <a href="../internal/config__get_audit_timezone/"><code>fabricops_kit.config._get_audit_timezone</code></a>
