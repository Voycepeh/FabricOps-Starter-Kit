# _render_custom_fields

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

Create widgets for configured organization-specific fields.

## Signature if available

```python
def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None=None) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._render_custom_fields`
- Short name: `_render_custom_fields`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/769c8a7851b5cc8730434576fb06702a5a032f26/src/fabricops_kit/data_agreement.py#L310-L359">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>

## Outbound references
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/data_agreement__to_bool/"><code>fabricops_kit.data_agreement._to_bool</code></a>
- <a href="../internal/data_agreement__widget_common/"><code>fabricops_kit.data_agreement._widget_common</code></a>
