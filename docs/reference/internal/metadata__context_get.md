# _context_get

**Module:** `metadata`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__resolve_action_by/"><code>fabricops_kit.metadata._resolve_action_by</code></a>
- <a href="../internal/metadata__runtime_context/"><code>fabricops_kit.metadata._runtime_context</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _context_get(context: Any, *keys: str) -> Any
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._context_get`
- Short name: `_context_get`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a212c94775e71b6e429e41b51fbc57ac733903cb/src/fabricops_kit/metadata.py#L172-L184">View source on GitHub</a>
- Inbound references count: 5
- Outbound references count: 0

## Inbound references
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__resolve_action_by/"><code>fabricops_kit.metadata._resolve_action_by</code></a>
- <a href="../internal/metadata__runtime_context/"><code>fabricops_kit.metadata._runtime_context</code></a>
