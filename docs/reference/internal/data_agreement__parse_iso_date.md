# _parse_iso_date

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
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>

## Purpose

Return an ISO date string or raise a clear intake validation error.

## Signature if available

```python
def _parse_iso_date(value: Any, field_name: str, *, required: bool=False) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._parse_iso_date`
- Short name: `_parse_iso_date`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/data_agreement.py#L572-L582">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 0

## Inbound references
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
