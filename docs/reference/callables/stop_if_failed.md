# stop_if_failed

**Module:** `drift`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Stop a notebook only when a schema or data-change guardrail result blocks continuation.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def stop_if_failed(result) -> None
```

## Parameters

result : dict
    Direct schema result, direct data-change result, or the wrapper returned
    by :func:`monitor_data_changes`.

## Returns

Not documented yet

## Raises

SchemaDriftError
    If the resolved result has ``can_continue=False``.

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline`; segment: `Guardrail enforcement`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/drift_SchemaDriftError/"><code>fabricops_kit.drift.SchemaDriftError</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="../../api/modules/drift/#stop_if_failed">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.drift.stop_if_failed`
- Short name: `stop_if_failed`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Inbound references count: 0
- Outbound references count: 1

## Outbound references
- <a href="../internal/drift_SchemaDriftError/"><code>fabricops_kit.drift.SchemaDriftError</code></a>
