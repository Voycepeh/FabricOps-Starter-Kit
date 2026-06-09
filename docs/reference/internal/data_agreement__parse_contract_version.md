# _parse_contract_version

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
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__next_minor_version/"><code>fabricops_kit.data_agreement._next_minor_version</code></a>

## Purpose

Parse a semantic contract version into a comparable tuple.

## Signature if available

```python
def _parse_contract_version(version: Any) -> tuple[int, int, int]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._parse_contract_version`
- Short name: `_parse_contract_version`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3d2707796405a2e3e2f36d7a599be05589995508/src/fabricops_kit/data_agreement.py#L638-L644">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 0

## Inbound references
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__next_minor_version/"><code>fabricops_kit.data_agreement._next_minor_version</code></a>
