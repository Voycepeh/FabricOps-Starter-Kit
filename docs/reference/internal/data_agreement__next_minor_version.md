# _next_minor_version

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__agreement_identity_text/"><code>fabricops_kit.data_agreement._agreement_identity_text</code></a>
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>

## Purpose

Return the next minor contract version, defaulting to ``1.

## Signature if available

```python
def _next_minor_version(version: Any) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._next_minor_version`
- Short name: `_next_minor_version`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/data_agreement.py#L647-L650">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 1

## Inbound references
- <a href="../internal/data_agreement__agreement_identity_text/"><code>fabricops_kit.data_agreement._agreement_identity_text</code></a>
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>

## Outbound references
- <a href="../internal/data_agreement__parse_contract_version/"><code>fabricops_kit.data_agreement._parse_contract_version</code></a>
