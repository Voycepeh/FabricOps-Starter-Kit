# _list_all_data_agreement_rows

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
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

## Purpose

List all append-only agreement rows from the metadata lakehouse.

## Signature if available

```python
def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any=None, missing_ok: bool=False) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._list_all_data_agreement_rows`
- Short name: `_list_all_data_agreement_rows`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6e744d11e5f3081af2c7f10e6b37ccaaba97dd6d/src/fabricops_kit/data_agreement.py#L672-L681">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 3

## Inbound references
- <a href="../internal/data_agreement__create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

## Outbound references
- <a href="../internal/data_agreement__coerce_row_dicts/"><code>fabricops_kit.data_agreement._coerce_row_dicts</code></a>
- <a href="../internal/data_agreement__config_value/"><code>fabricops_kit.data_agreement._config_value</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
