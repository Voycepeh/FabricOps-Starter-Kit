# _save_agreement_evidence_records

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

## Purpose

Append manually uploaded evidence file-reference metadata rows.

## Signature if available

```python
def _save_agreement_evidence_records(*, spark: Any, config: Any, env_name: str, agreement_id: str, contract_version: str, evidence_type: str, evidence_file_paths: Any, committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._save_agreement_evidence_records`
- Short name: `_save_agreement_evidence_records`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c30f90cb0288be7f5624f9a80a62facf8b12c3e5/src/fabricops_kit/data_agreement.py#L822-L853">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

## Outbound references
- <a href="../internal/data_agreement__config_value/"><code>fabricops_kit.data_agreement._config_value</code></a>
- <a href="../internal/data_agreement__prepare_evidence_file_references/"><code>fabricops_kit.data_agreement._prepare_evidence_file_references</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
