# _render_agreement_evidence_widget

**Module:** `data_agreement`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../widget_render_agreement_evidence/"><code>fabricops_kit.data_agreement.widget_render_agreement_evidence</code></a>

## Purpose

Render optional agreement evidence upload controls.

## Signature if available

```python
def _render_agreement_evidence_widget(*, spark: Any, config: Any, env_name: str, display_widget: bool=True) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._render_agreement_evidence_widget`
- Short name: `_render_agreement_evidence_widget`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/data_agreement.py#L1341-L1459">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 5

## Inbound references
- <a href="../widget_render_agreement_evidence/"><code>fabricops_kit.data_agreement.widget_render_agreement_evidence</code></a>

## Outbound references
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/data_agreement__save_agreement_evidence_records/"><code>fabricops_kit.data_agreement._save_agreement_evidence_records</code></a>
- <a href="../internal/data_agreement__widget_common/"><code>fabricops_kit.data_agreement._widget_common</code></a>
