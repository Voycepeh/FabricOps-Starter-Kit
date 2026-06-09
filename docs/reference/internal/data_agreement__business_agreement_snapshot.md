# _business_agreement_snapshot

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>

## Purpose

Return user-facing agreement values used to detect business changes.

## Signature if available

```python
def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._business_agreement_snapshot`
- Short name: `_business_agreement_snapshot`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5d3d97d1ce1ae47231e3567728d98d9a77733d95/src/fabricops_kit/data_agreement.py#L704-L708">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>

## Outbound references
- <a href="../internal/data_agreement__deserialize_custom_fields/"><code>fabricops_kit.data_agreement._deserialize_custom_fields</code></a>
- <a href="../internal/data_agreement__serialize_custom_fields/"><code>fabricops_kit.data_agreement._serialize_custom_fields</code></a>
