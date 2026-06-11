# _build_runtime_audit_fields

**Module:** `metadata`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement__save_agreement_evidence_records/"><code>fabricops_kit.data_agreement._save_agreement_evidence_records</code></a>
- <a href="../internal/governance_review__approved_review_context/"><code>fabricops_kit.governance_review._approved_review_context</code></a>
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

## Purpose

Build reusable framework-managed audit fields for metadata-table rows.

## Signature if available

```python
def _build_runtime_audit_fields(*, config: Any=None, env: str | None=None, timestamp_field: str='_committed_at', user_field: str='_committed_by', workspace_field: str='_workspace_name', notebook_field: str='_notebook_name', metadata_lakehouse_field: str='_metadata_lakehouse_name', activity_field: str='_activity_id', committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._build_runtime_audit_fields`
- Short name: `_build_runtime_audit_fields`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/metadata.py#L219-L289">View source on GitHub</a>
- Inbound references count: 6
- Outbound references count: 4

## Inbound references
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement__save_agreement_evidence_records/"><code>fabricops_kit.data_agreement._save_agreement_evidence_records</code></a>
- <a href="../internal/governance_review__approved_review_context/"><code>fabricops_kit.governance_review._approved_review_context</code></a>
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>
- <a href="../internal/pipeline__runtime_audit_fields/"><code>fabricops_kit.pipeline._runtime_audit_fields</code></a>

## Outbound references
- <a href="../internal/config__current_audit_timestamp/"><code>fabricops_kit.config._current_audit_timestamp</code></a>
- <a href="../internal/metadata__context_get/"><code>fabricops_kit.metadata._context_get</code></a>
- <a href="../internal/metadata__runtime_context/"><code>fabricops_kit.metadata._runtime_context</code></a>
- <a href="../internal/metadata__safe_str/"><code>fabricops_kit.metadata._safe_str</code></a>
