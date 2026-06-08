# review_pipeline_run

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use in 03_review after 02_pipeline has written metadata evidence and a reviewer needs an approved, rejected, or needs_remediation outcome.

## When not to use this

Do not use before 02_pipeline evidence exists, as a replacement for agreement intake, or to make pipeline writes.

## Quick example

review = review_pipeline_run(CONFIG, ENV, spark_session=spark, dataset_name=DATASET_NAME, target_table=TARGET_TABLE)

## Signature

```python
def review_pipeline_run(config: Any, env: str, *, spark_session: Any, dataset_name: str, target_table: str, run_id: str | None=None, agreement_id: str | None=None, reviewed_by: str | None=None, mode: str='append') -> dict[str, Any]
```

## Parameters

config, env, spark_session, dataset_name, target_table, optional run_id, agreement_id, reviewed_by, and mode.

## Returns

Governance review row with outcome and evidence status fields.

## Raises

Raises metadata read/write errors when configured metadata tables are unavailable.

## Side effects

Reads agreement, profile, lineage, DQ, and pipeline-run metadata; appends one row to METADATA_GOVERNANCE_REVIEW.

## FabricOps context

Requires 00_env_config metadata routing and a separate 03_review session with access to the metadata lakehouse.

## AI implementation contract

- **required_context:** Requires 00_env_config metadata routing and a separate 03_review session with access to the metadata lakehouse.
- **inputs:** config, env, spark_session, dataset_name, target_table, optional run_id, agreement_id, reviewed_by, and mode.
- **output:** Governance review row with outcome and evidence status fields.
- **side_effects:** Reads agreement, profile, lineage, DQ, and pipeline-run metadata; appends one row to METADATA_GOVERNANCE_REVIEW.
- **failure_modes:** Raises metadata read/write errors when configured metadata tables are unavailable.
- **verification:** Confirm the outcome and issues_json reflect missing agreement evidence, failed DQ, and schema drift before treating the review as complete.

## Related functions

- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#review_pipeline_run">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.review_pipeline_run`
- Short name: `review_pipeline_run`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Inbound references count: 0
- Outbound references count: 10

## Outbound references
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review__dq_review_status/"><code>fabricops_kit.governance_review._dq_review_status</code></a>
- <a href="../internal/governance_review__governance_outcome/"><code>fabricops_kit.governance_review._governance_outcome</code></a>
- <a href="../internal/governance_review__latest_row/"><code>fabricops_kit.governance_review._latest_row</code></a>
- <a href="../internal/governance_review__matches_identity/"><code>fabricops_kit.governance_review._matches_identity</code></a>
- <a href="../internal/governance_review__read_metadata_rows/"><code>fabricops_kit.governance_review._read_metadata_rows</code></a>
- <a href="../internal/governance_review__schema_review_status/"><code>fabricops_kit.governance_review._schema_review_status</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/metadata__resolve_action_by/"><code>fabricops_kit.metadata._resolve_action_by</code></a>
