# _registry_rows_with_defaults

**Module:** `metadata`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _registry_rows_with_defaults(rows: Any) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._registry_rows_with_defaults`
- Short name: `_registry_rows_with_defaults`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6d8de4b3e35399458b9ee2a79568a6d6f1831a4e/src/fabricops_kit/metadata.py#L407-L418">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 3

## Inbound references
- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

## Outbound references
- <a href="../internal/metadata__coerce_row_dicts/"><code>fabricops_kit.metadata._coerce_row_dicts</code></a>
- <a href="../internal/metadata__notebook_registration_key/"><code>fabricops_kit.metadata._notebook_registration_key</code></a>
- <a href="../internal/metadata__safe_str/"><code>fabricops_kit.metadata._safe_str</code></a>
