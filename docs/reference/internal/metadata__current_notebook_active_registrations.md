# _current_notebook_active_registrations

**Module:** `metadata`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Purpose

Return active agreement registrations for the running notebook.

## Signature if available

```python
def _current_notebook_active_registrations(spark, *, config: Any, env: str, metadata_table: str=NOTEBOOK_REGISTRY_TABLE, notebook_type: str | None=None, environment_name: str | None=None, registration_role: str | None=None, missing_ok: bool=True) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._current_notebook_active_registrations`
- Short name: `_current_notebook_active_registrations`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/769c8a7851b5cc8730434576fb06702a5a032f26/src/fabricops_kit/metadata.py#L475-L525">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Outbound references
- <a href="../internal/metadata__context_get/"><code>fabricops_kit.metadata._context_get</code></a>
- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__runtime_context/"><code>fabricops_kit.metadata._runtime_context</code></a>
- <a href="../internal/metadata__safe_str/"><code>fabricops_kit.metadata._safe_str</code></a>
