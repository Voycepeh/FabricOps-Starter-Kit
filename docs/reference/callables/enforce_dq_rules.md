# enforce_dq_rules

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use before target writes to enforce active approved DQ rules for a dataset/table as a pipeline guardrail.

## When not to use this

Do not use to filter bad rows, author new DQ rules, or bypass governance review approval.

## Quick example

dq_result = enforce_dq_rules(df, CONFIG, env, dataset_name, table_name, spark_session=spark)
stop_if_failed(dq_result)

## Signature

```python
def enforce_dq_rules(dataframe, config, env, dataset_name, table_name, *, spark_session=None) -> dict
```

## Parameters

dataframe, config, env, dataset_name, table_name, and optional spark_session.

## Returns

Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.

## Raises

Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.

## Side effects

Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.

## FabricOps context

Requires active approved DQ-rule evidence in the configured metadata target from 03_review governance workflows.

## AI implementation contract

- **required_context:** Requires active approved DQ-rule evidence in the configured metadata target from 03_review governance workflows.
- **inputs:** dataframe, config, env, dataset_name, table_name, and optional spark_session.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.
- **side_effects:** Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.
- **failure_modes:** Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.
- **verification:** Verify approved metadata exists, inspect status/can_continue, and call stop_if_failed before writing when blocking failures occur.

## Related functions

- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#enforce_dq_rules">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.enforce_dq_rules`
- Short name: `enforce_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Inbound references count: 0
- Outbound references count: 7

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_summary/"><code>fabricops_kit.governance_review._dq_summary</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__summarize_dq_guardrail/"><code>fabricops_kit.governance_review._summarize_dq_guardrail</code></a>
