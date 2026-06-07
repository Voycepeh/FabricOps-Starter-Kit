# _prepare_evidence_file_references

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__save_agreement_evidence_records/"><code>fabricops_kit.data_agreement._save_agreement_evidence_records</code></a>

## Purpose

Parse and validate manually supplied evidence file paths before writes.

## Signature if available

```python
def _prepare_evidence_file_references(paths_value: Any) -> list[dict[str, str]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._prepare_evidence_file_references`
- Short name: `_prepare_evidence_file_references`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1171b98e11e7afc7b6351c6501d1c7050119657f/src/fabricops_kit/data_agreement.py#L770-L820">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../internal/data_agreement__save_agreement_evidence_records/"><code>fabricops_kit.data_agreement._save_agreement_evidence_records</code></a>

## Outbound references
- <a href="../internal/data_agreement__get_notebookutils/"><code>fabricops_kit.data_agreement._get_notebookutils</code></a>
