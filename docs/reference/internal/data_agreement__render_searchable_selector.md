# _render_searchable_selector

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Purpose

Render a table-backed selector with search and stable-value tracking.

## Signature if available

```python
def _render_searchable_selector(*, widgets: Any, label: str, rows: list[dict[str, Any]], label_fn: Callable[[dict[str, Any]], str], value_fn: Callable[[dict[str, Any]], str], placeholder: str='Search...', max_results: int=25, search_fields: list[str] | None=None, context_fields: list[tuple[str, str]] | None=None, empty_label: str | None=None, selected_value: str | None=None) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._render_searchable_selector`
- Short name: `_render_searchable_selector`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ffb9386812c13cf40a6a40503d36bd7a16dc5e31/src/fabricops_kit/data_agreement.py#L198-L308">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 2

## Inbound references
- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Outbound references
- <a href="../internal/data_agreement__html_escape/"><code>fabricops_kit.data_agreement._html_escape</code></a>
- <a href="../internal/data_agreement__widget_common/"><code>fabricops_kit.data_agreement._widget_common</code></a>
