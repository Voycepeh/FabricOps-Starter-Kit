# stop_if_failed

**Module:** `drift`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use after schema, drift, or DQ guardrail helpers to stop the notebook when can_continue is false.

## When not to use this

Do not use for informational warnings that should not block execution, or before a guardrail result exists.

## Quick example

schema_result = validate_schema(df, expected_schema)
stop_if_failed(schema_result)

## Signature

```python
def stop_if_failed(result) -> None
```

## Parameters

guardrail result dictionary and optional message/runtime controls.

## Returns

None when execution may continue; otherwise raises or exits according to runtime behavior.

## Raises

Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail must stop execution.

## Side effects

May terminate notebook execution through Fabric notebook utilities or raise an exception.

## FabricOps context

Use in 02_pipeline after validate_schema, monitor_data_changes, or enforce_dq_rules and before write helpers.

## AI implementation contract

- **required_context:** Use in 02_pipeline after validate_schema, monitor_data_changes, or enforce_dq_rules and before write helpers.
- **inputs:** guardrail result dictionary and optional message/runtime controls.
- **output:** None when execution may continue; otherwise raises or exits according to runtime behavior.
- **side_effects:** May terminate notebook execution through Fabric notebook utilities or raise an exception.
- **failure_modes:** Raises RuntimeError outside Fabric notebook exit handling when a failed guardrail must stop execution.
- **verification:** Verify the guardrail result shape includes status/can_continue/message before passing it to stop_if_failed.

## Related functions

- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

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
