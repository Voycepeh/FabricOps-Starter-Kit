# _review_governance_evidence

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

## Purpose

Review persisted v1 evidence and write a governance outcome row.

## Signature if available

```python
def _review_governance_evidence(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any, reviewed_by: str | None=None, mode: str='append') -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._review_governance_evidence`
- Short name: `_review_governance_evidence`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/governance_review.py#L566-L712">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 11

## Inbound references
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

## Outbound references
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__latest_row/"><code>fabricops_kit.governance_review._latest_row</code></a>
- <a href="../internal/governance_review__read_metadata_rows/"><code>fabricops_kit.governance_review._read_metadata_rows</code></a>
- <a href="../internal/governance_review__status_is_failed/"><code>fabricops_kit.governance_review._status_is_failed</code></a>
- <a href="../internal/governance_review__status_is_warning/"><code>fabricops_kit.governance_review._status_is_warning</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/metadata__now_utc_iso/"><code>fabricops_kit.metadata._now_utc_iso</code></a>
- <a href="../internal/metadata__resolve_action_by/"><code>fabricops_kit.metadata._resolve_action_by</code></a>
