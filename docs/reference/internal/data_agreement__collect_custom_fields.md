# _collect_custom_fields

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>

## Purpose

Collect and validate configured custom-field widget values.

## Signature if available

```python
def _collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._collect_custom_fields`
- Short name: `_collect_custom_fields`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/data_agreement.py#L362-L394">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>

## Outbound references
- <a href="../internal/data_agreement__to_iso_date/"><code>fabricops_kit.data_agreement._to_iso_date</code></a>
