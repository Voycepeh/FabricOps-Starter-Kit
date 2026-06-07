# validate_schema

**Module:** `drift`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def validate_schema(dataframe, expected_schema: dict[str, str], *, preset: str='strict') -> dict
```

## Parameters

dataframe : Any
    Spark, pandas, or dataframe-like object with schema metadata.
expected_schema : dict[str, str]
    Mapping of required column names to expected datatype strings.
preset : {"strict", "allow_new_columns", "monitor_only"}, default="strict"
    Schema validation intent. ``strict`` blocks missing columns, datatype
    changes, and unexpected columns. ``allow_new_columns`` blocks missing
    columns and datatype changes while reporting additional columns as a
    warning. ``monitor_only`` reports all differences without blocking.

## Returns

dict
    Standard guardrail result with ``status``, ``can_continue``,
    ``checks``, and ``message`` plus detailed schema difference fields.

## Raises

ValueError
    If ``preset`` is not one of the supported schema presets.

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline`; segment: `Schema validation`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/drift__actual_schema/"><code>fabricops_kit.drift._actual_schema</code></a>
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="../../api/modules/drift/#validate_schema">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.drift.validate_schema`
- Short name: `validate_schema`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Inbound references count: 0
- Outbound references count: 2

## Outbound references
- <a href="../internal/drift__actual_schema/"><code>fabricops_kit.drift._actual_schema</code></a>
- <a href="../internal/drift__normalize_datatype/"><code>fabricops_kit.drift._normalize_datatype</code></a>
