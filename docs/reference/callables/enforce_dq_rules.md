# enforce_dq_rules

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Enforce approved active DQ rules as a target-write guardrail without filtering rows.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def enforce_dq_rules(dataframe, config, env, dataset_name, table_name, *, spark_session=None) -> dict
```

## Parameters

dataframe : Any
    Spark DataFrame to evaluate before the target write. The full DataFrame
    is never filtered or split by this helper.
config : FrameworkConfig or dict
    Runtime configuration containing the configured metadata lakehouse
    route from ``00_env_config``.
env : str
    Environment name used to read ``METADATA_DQ_RULES`` from the configured
    metadata target.
dataset_name : str
    Dataset identifier used with ``table_name`` to scope approved DQ rules
    when those columns exist in the metadata table.
table_name : str
    Target table name whose approved active DQ rules should be enforced.
spark_session : pyspark.sql.SparkSession, optional
    Spark session used to read metadata when required by the configured
    storage helper.

## Returns

dict
    Guardrail result with ``status``, ``can_continue``, ``checks``, and
    ``message``. The result also carries the full tagged ``dataframe`` and
    aggregate ``summary`` fields for the existing catalogue evidence path.
    Error-severity rule failures return ``status='failed'`` and
    ``can_continue=False``. Warning-severity failures return
    ``status='warning'`` and ``can_continue=True``. Passing or absent rules
    return ``status='passed'`` and ``can_continue=True``.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline`; segment: `DQ guardrails`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__dq_failed_row_count/"><code>fabricops_kit.governance_review._dq_failed_row_count</code></a>
- <a href="../internal/governance_review__dq_summary/"><code>fabricops_kit.governance_review._dq_summary</code></a>
- <a href="../internal/governance_review__dq_tagged_dataframe/"><code>fabricops_kit.governance_review._dq_tagged_dataframe</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__summarize_dq_guardrail/"><code>fabricops_kit.governance_review._summarize_dq_guardrail</code></a>

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
