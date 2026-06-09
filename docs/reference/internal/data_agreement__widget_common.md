# _widget_common

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
- <a href="../internal/data_agreement__render_custom_fields/"><code>fabricops_kit.data_agreement._render_custom_fields</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__standard_widget/"><code>fabricops_kit.data_agreement._standard_widget</code></a>

## Purpose

Return common style and layout keyword arguments for form controls.

## Signature if available

```python
def _widget_common(widgets_module: Any, description: str, *, textarea: bool=False) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._widget_common`
- Short name: `_widget_common`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/data_agreement.py#L180-L189">View source on GitHub</a>
- Inbound references count: 4
- Outbound references count: 0

## Inbound references
- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>
- <a href="../internal/data_agreement__render_custom_fields/"><code>fabricops_kit.data_agreement._render_custom_fields</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__standard_widget/"><code>fabricops_kit.data_agreement._standard_widget</code></a>
