# _load_notebook_registry

**Module:** `metadata`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _load_notebook_registry(spark, agreement_id=None, metadata_table=NOTEBOOK_REGISTRY_TABLE, notebook_type=None, environment_name=None, missing_ok: bool=True, *, config: Any=None, env: str | None=None, active_only: bool=False, notebook_id: str | None=None, notebook_name: str | None=None, registration_role: str | None=None) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._load_notebook_registry`
- Short name: `_load_notebook_registry`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/metadata.py#L422-L473">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 3

## Inbound references
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/metadata__notebook_registration_key/"><code>fabricops_kit.metadata._notebook_registration_key</code></a>
- <a href="../internal/metadata__registry_rows_with_defaults/"><code>fabricops_kit.metadata._registry_rows_with_defaults</code></a>
