# _render_maintenance_widget

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../widget_render_data_agreement/"><code>fabricops_kit.data_agreement.widget_render_data_agreement</code></a>
- <a href="../widget_render_data_steward/"><code>fabricops_kit.data_agreement.widget_render_data_steward</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str, display_widget: bool=True) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._render_maintenance_widget`
- Short name: `_render_maintenance_widget`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/data_agreement.py#L1130-L1338">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 15

## Inbound references
- <a href="../widget_render_data_agreement/"><code>fabricops_kit.data_agreement.widget_render_data_agreement</code></a>
- <a href="../widget_render_data_steward/"><code>fabricops_kit.data_agreement.widget_render_data_steward</code></a>

## Outbound references
- <a href="../internal/data_agreement__agreement_identity_text/"><code>fabricops_kit.data_agreement._agreement_identity_text</code></a>
- <a href="../internal/data_agreement__collect_custom_fields/"><code>fabricops_kit.data_agreement._collect_custom_fields</code></a>
- <a href="../internal/data_agreement__config_value/"><code>fabricops_kit.data_agreement._config_value</code></a>
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement__deserialize_custom_fields/"><code>fabricops_kit.data_agreement._deserialize_custom_fields</code></a>
- <a href="../internal/data_agreement__get_widget_visible_fields/"><code>fabricops_kit.data_agreement._get_widget_visible_fields</code></a>
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/data_agreement__render_custom_fields/"><code>fabricops_kit.data_agreement._render_custom_fields</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/data_agreement__standard_widget/"><code>fabricops_kit.data_agreement._standard_widget</code></a>
- <a href="../internal/data_agreement__to_bool/"><code>fabricops_kit.data_agreement._to_bool</code></a>
- <a href="../internal/data_agreement__to_iso_date/"><code>fabricops_kit.data_agreement._to_iso_date</code></a>
