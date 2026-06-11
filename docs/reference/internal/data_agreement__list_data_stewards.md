# _list_data_stewards

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
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>

## Purpose

List latest append-only steward rows from the metadata lakehouse.

## Signature if available

```python
def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=True, missing_ok: bool=False) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._list_data_stewards`
- Short name: `_list_data_stewards`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/data_agreement.py#L536-L565">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 4

## Inbound references
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>

## Outbound references
- <a href="../internal/data_agreement__active_steward/"><code>fabricops_kit.data_agreement._active_steward</code></a>
- <a href="../internal/data_agreement__config_value/"><code>fabricops_kit.data_agreement._config_value</code></a>
- <a href="../internal/data_agreement__latest_by_key/"><code>fabricops_kit.data_agreement._latest_by_key</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
