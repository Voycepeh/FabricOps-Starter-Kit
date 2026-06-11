# _to_bool

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__active_steward/"><code>fabricops_kit.data_agreement._active_steward</code></a>
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement__render_custom_fields/"><code>fabricops_kit.data_agreement._render_custom_fields</code></a>
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../internal/data_agreement__standard_widget/"><code>fabricops_kit.data_agreement._standard_widget</code></a>

## Purpose

Normalize common notebook and metadata boolean representations.

## Signature if available

```python
def _to_bool(value: Any) -> bool
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._to_bool`
- Short name: `_to_bool`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a212c94775e71b6e429e41b51fbc57ac733903cb/src/fabricops_kit/data_agreement.py#L497-L513">View source on GitHub</a>
- Inbound references count: 5
- Outbound references count: 0

## Inbound references
- <a href="../internal/data_agreement__active_steward/"><code>fabricops_kit.data_agreement._active_steward</code></a>
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement__render_custom_fields/"><code>fabricops_kit.data_agreement._render_custom_fields</code></a>
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../internal/data_agreement__standard_widget/"><code>fabricops_kit.data_agreement._standard_widget</code></a>
