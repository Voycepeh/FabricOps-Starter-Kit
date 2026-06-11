# _create_or_update_data_agreement

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

Append a new agreement or a new semantic version of an existing one.

## Signature if available

```python
def _create_or_update_data_agreement(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None=None, custom_fields: dict[str, Any] | None=None, committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._create_or_update_data_agreement`
- Short name: `_create_or_update_data_agreement`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a212c94775e71b6e429e41b51fbc57ac733903cb/src/fabricops_kit/data_agreement.py#L711-L755">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 11

## Inbound references
- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>

## Outbound references
- <a href="../internal/data_agreement__business_agreement_snapshot/"><code>fabricops_kit.data_agreement._business_agreement_snapshot</code></a>
- <a href="../internal/data_agreement__config_value/"><code>fabricops_kit.data_agreement._config_value</code></a>
- <a href="../internal/data_agreement__generate_agreement_id/"><code>fabricops_kit.data_agreement._generate_agreement_id</code></a>
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/data_agreement__next_minor_version/"><code>fabricops_kit.data_agreement._next_minor_version</code></a>
- <a href="../internal/data_agreement__parse_contract_version/"><code>fabricops_kit.data_agreement._parse_contract_version</code></a>
- <a href="../internal/data_agreement__parse_iso_date/"><code>fabricops_kit.data_agreement._parse_iso_date</code></a>
- <a href="../internal/data_agreement__serialize_custom_fields/"><code>fabricops_kit.data_agreement._serialize_custom_fields</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
