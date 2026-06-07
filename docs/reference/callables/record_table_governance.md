# record_table_governance

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def record_table_governance(config: Any, env: str, profile_rows: list[dict[str, Any]], *, spark_session: Any, context_reviews: list[dict[str, Any]] | None=None, dq_rule_reviews: list[dict[str, Any]] | None=None, classification_reviews: list[dict[str, Any]] | None=None, approved_by: str | None=None, mode: str='append') -> dict[str, list[dict[str, Any]]]
```

## Parameters

config : FrameworkConfig or dict
    Shared ``00_env_config`` configuration that routes metadata writes to
    the configured metadata lakehouse target.
env : str
    Environment key in ``config``.
profile_rows : list of dict
    Column-profile rows loaded for the selected catalogue table.
spark_session : pyspark.sql.SparkSession
    Spark session used to create DataFrames for metadata writes.
context_reviews, dq_rule_reviews, classification_reviews : list of dict, optional
    Human-approved rows from the governance review workflow. Only rows with
    ``review_status="approved"`` and ``commit=True`` are written.
approved_by : str, optional
    Reviewer identity to stamp on records. When omitted, runtime defaults
    are used.
mode : str, default "append"
    Write mode for metadata table commits.

## Returns

dict[str, list[dict[str, Any]]]
    Records written for ``column_context``, ``dq_rules``, and
    ``column_classification``.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `03_review`; segment: `Governance review`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#record_table_governance">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.record_table_governance`
- Short name: `record_table_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>
