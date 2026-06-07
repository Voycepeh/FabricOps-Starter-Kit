# validate_schema

**Module:** `drift`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use before writes to compare a DataFrame schema against an expected schema with strict, allow-new-columns, or monitor-only behavior.

## When not to use this

Do not use for data-value drift, DQ-rule enforcement, or metadata persistence.

## Quick example

schema_result = validate_schema(df, {"order_id": "string"}, preset="allow_new_columns")
stop_if_failed(schema_result)

## Signature

```python
def validate_schema(dataframe, expected_schema: dict[str, str], *, preset: str='strict') -> dict
```

## Parameters

dataframe, expected_schema mapping, and preset controlling blocking behavior.

## Returns

Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.

## Raises

ValueError when preset is not one of the supported schema presets.

## Side effects

Inspects DataFrame schema only; it does not write metadata, tables, or files.

## FabricOps context

Use in 02_pipeline before write helpers so schema guardrails run before publishing data.

## AI implementation contract

- **required_context:** Use in 02_pipeline before write helpers so schema guardrails run before publishing data.
- **inputs:** dataframe, expected_schema mapping, and preset controlling blocking behavior.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, and schema difference details.
- **side_effects:** Inspects DataFrame schema only; it does not write metadata, tables, or files.
- **failure_modes:** ValueError when preset is not one of the supported schema presets.
- **verification:** Verify can_continue before calling write helpers and pass the result to stop_if_failed when blocking behavior is required.

## Related functions

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

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
