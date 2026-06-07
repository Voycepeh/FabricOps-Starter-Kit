# record_table_governance

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use in 03_review after human approval to persist approved column context, DQ rules, and classification evidence for a profiled table.

## When not to use this

Do not use to draft governance recommendations, bypass review approval, or write unapproved rows.

## Quick example

written = record_table_governance(CONFIG, env, profile_rows, spark_session=spark, context_reviews=context_rows, dq_rule_reviews=dq_rows, classification_reviews=classification_rows, approved_by="reviewer")

## Signature

```python
def record_table_governance(config: Any, env: str, profile_rows: list[dict[str, Any]], *, spark_session: Any, context_reviews: list[dict[str, Any]] | None=None, dq_rule_reviews: list[dict[str, Any]] | None=None, classification_reviews: list[dict[str, Any]] | None=None, approved_by: str | None=None, mode: str='append') -> dict[str, list[dict[str, Any]]]
```

## Parameters

config, env, profile_rows, spark_session, optional approved context/DQ/classification review rows, approved_by, and mode.

## Returns

Dictionary of records written for column_context, dq_rules, and column_classification.

## Raises

Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.

## Side effects

Writes approved governance metadata records to configured metadata tables.

## FabricOps context

Requires 03_review profile rows and 00_env_config metadata routing; governance metadata must be written to the configured metadata target.

## AI implementation contract

- **required_context:** Requires 03_review profile rows and 00_env_config metadata routing; governance metadata must be written to the configured metadata target.
- **inputs:** config, env, profile_rows, spark_session, optional approved context/DQ/classification review rows, approved_by, and mode.
- **output:** Dictionary of records written for column_context, dq_rules, and column_classification.
- **side_effects:** Writes approved governance metadata records to configured metadata tables.
- **failure_modes:** Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.
- **verification:** Verify review_status is approved and commit is true for intended rows before calling; confirm returned record groups match expected approvals.

## Related functions

- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

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
