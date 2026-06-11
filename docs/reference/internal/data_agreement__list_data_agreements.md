# _list_data_agreements

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
- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Purpose

List latest versioned agreements from the configured metadata lakehouse.

## Signature if available

```python
def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=False, missing_ok: bool=False) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._list_data_agreements`
- Short name: `_list_data_agreements`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/data_agreement.py#L684-L691">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Outbound references
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
