# monitor_data_changes

**Module:** `drift`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use in 02_pipeline to compare current profile evidence with an approved or previous baseline and produce a data-change guardrail result.

## When not to use this

Do not use for simple schema validation or DQ-rule enforcement; use validate_schema or enforce_dq_rules for those checks.

## Quick example

drift_result = monitor_data_changes(spark, df, "METADATA_PROFILE", dataset_name, table_name, stage="target")
stop_if_failed(drift_result)

## Signature

```python
def monitor_data_changes(spark, dataframe, metadata_table: str, dataset_name: str, table_name: str, *, stage: str, preset: str='changing_data', exclude_run_id: str | None=None, distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None, policy_overrides: dict | None=None) -> dict
```

## Parameters

spark, dataframe, metadata_table, dataset_name, table_name, required stage, preset, optional exclude_run_id, distribution columns, and policy overrides.

## Returns

Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and drift checks.

## Raises

Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.

## Side effects

Reads baseline profile metadata and computes current profile evidence; it does not write target data.

## FabricOps context

Requires profile metadata routed through the configured 00_env_config metadata target and a valid source/target stage.

## AI implementation contract

- **required_context:** Requires profile metadata routed through the configured 00_env_config metadata target and a valid source/target stage.
- **inputs:** spark, dataframe, metadata_table, dataset_name, table_name, required stage, preset, optional exclude_run_id, distribution columns, and policy overrides.
- **output:** Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and drift checks.
- **side_effects:** Reads baseline profile metadata and computes current profile evidence; it does not write target data.
- **failure_modes:** Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.
- **verification:** Verify baseline selection, status, and can_continue before allowing downstream writes or calling stop_if_failed.

## Related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="../../api/modules/drift/#monitor_data_changes">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.drift.monitor_data_changes`
- Short name: `monitor_data_changes`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Inbound references count: 0
- Outbound references count: 6

## Outbound references
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__baseline_distribution_args/"><code>fabricops_kit.drift._baseline_distribution_args</code></a>
- <a href="../internal/drift__check_profile_drift/"><code>fabricops_kit.drift._check_profile_drift</code></a>
- <a href="../internal/drift__data_change_preset_config/"><code>fabricops_kit.drift._data_change_preset_config</code></a>
- <a href="../internal/drift__load_latest_profile/"><code>fabricops_kit.drift._load_latest_profile</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>
