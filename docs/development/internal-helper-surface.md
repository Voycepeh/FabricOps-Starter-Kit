# Internal helper surface audit

This page records focused cleanup notes for helper-heavy modules. It is a handover aid for reviewers and future maintainers; generated API reference pages remain sourced from code metadata and docstrings.

## `src/fabricops_kit/drift.py`

### Scope and public surface

- Public v1 callable count before: 3 (`validate_schema`, `monitor_data_changes`, `stop_if_failed`).
- Public v1 callable count after: 3 (`validate_schema`, `monitor_data_changes`, `stop_if_failed`).
- Internal helper count before: 41 underscore-prefixed helper functions.
- Internal helper count after: 14 underscore-prefixed helper functions.

### Deleted functions

Removed unused advanced partition, incremental-safety, evidence, and summary paths that were not active in the v1 notebook guardrail flow:

- `_detect_dataframe_engine`
- `_utc_now_iso`
- `_safe_spark_collect`
- `_json_dumps`
- `_write_metadata_rows`
- `_check_partition_drift`
- `_build_and_write_partition_snapshot`
- `_load_latest_partition_snapshot`
- `_summarize_drift_results`
- `_build_drift_evidence_record`
- `_prepare_drift_baselines`
- `_default_incremental_safety_policy`
- `_hash`
- `_build_partition_hash`
- `_build_pandas_partition_snapshot`
- `_build_spark_partition_snapshot`
- `_build_partition_snapshot`
- `_is_closed_partition`
- `_compare_partition_snapshots`
- `_assert_incremental_safe`
- `_build_incremental_safety_records`

### Compatibility classes restored

- `UnsupportedDataFrameEngineError` remains import-compatible for previously documented internal dataframe-engine imports, but the removed engine-detection helper path was not restored.
- `IncrementalSafetyError` remains import-compatible for previously documented internal incremental-safety imports, but the removed incremental helper path was not restored.

### Merged helpers

- `_default_profile_drift_policy` was replaced with `_DEFAULT_PROFILE_DRIFT_POLICY` so direct profile-drift checks and data-change presets share a simple threshold constant instead of a function wrapper.
- `_normalize_baseline_mode` was merged into `_load_latest_profile`, where baseline mode validation is used.
- `_as_monitor_only_result` was merged into `monitor_data_changes`, keeping monitor-only behavior next to preset resolution and the final guardrail result shape.

### Inlined helpers

- `_check_schema` was inlined into `validate_schema`, leaving schema enforcement in one public guardrail entrypoint while preserving expected-schema, preset, and datatype comparison behavior.
- `_profile_check_status` was inlined into numeric PSI and categorical-distance checks because it only encoded a two-threshold status decision at the call sites.
- `_assert_no_blocking_profile_drift` was removed in favor of `stop_if_failed`, which remains the single public stop mechanism for guardrail result objects.

### Helpers intentionally kept

- `_normalize_datatype`: preserves Spark/pandas datatype alias handling for schema validation.
- `_actual_schema`: isolates Spark/pandas/dataframe-like schema extraction.
- `_row_get`: normalizes dictionary, Spark Row, and object-style metadata row access.
- `_parse_distribution`: safely parses JSON distribution payloads from profile metadata.
- `_normalize_profile`: keeps profile dictionaries, Spark DataFrames, and collected rows in one comparison shape.
- `_extract_numeric_distribution_bin_edges`: reuses baseline numeric bins so current profiles remain comparable.
- `_extract_categorical_distribution_categories`: reuses baseline categories so categorical comparisons can identify new categories.
- `_proportions`: supports PSI calculation with zero-count protection.
- `_numeric_psi`: implements numeric distribution drift scoring.
- `_categorical_distance`: implements categorical distribution drift scoring and new-category reporting.
- `_check_profile_drift`: compares normalized profiles against row-count, null, distinct, PSI, and categorical thresholds.
- `_is_missing_table_error`: treats missing metadata tables as no-baseline rather than runtime failures.
- `_load_latest_profile`: selects latest successful or approved profile baselines from metadata.
- `_data_change_preset_config`: validates presets and threshold overrides while preserving user configurability.
# Internal helper surface

This page records focused internal-helper cleanup decisions so future PRs can avoid reintroducing wrapper chains or legacy widget scaffolding.

## `src/fabricops_kit/governance_review.py`

### Counts

| Metric | Before | After | Notes |
| --- | ---: | ---: | --- |
| Public v1 callables | 7 | 7 | The supported notebook-facing surface is unchanged. |
| Internal helper functions | 24 | 15 | Removed dead helpers, wrapper-only commit helpers, and obsolete combined-widget support. |

### Public callables kept stable

- `widget_select_catalogue_table`
- `get_selected_catalogue_table`
- `load_catalogue_profile_rows`
- `widget_review_column_context`
- `widget_review_dq_rules`
- `widget_review_column_classification`
- `record_table_governance`

### Functions deleted

- `_build_profile_summary` — dead display-only summary helper with no notebook or package callers.
- `_latest_by_column` — legacy latest-approved-state helper tied to earlier combined review flows.
- `_optional_ai_generate_response` — dead Fabric AI wrapper not used by the standalone v1 review widgets.
- `_widget_review_table_governance` — obsolete combined-widget implementation that must not return as public v1 API.

### Functions merged

- `_commit_column_context`, `_commit_dq_rules`, and `_commit_column_classification` were merged into the consolidated backend commit loop in `record_table_governance`.

### Functions inlined

- `_audit` was inlined into the row builders by calling `_build_runtime_audit_fields` directly when commit metadata is available.
- `_row_metadata_table_key` was inlined into `load_catalogue_profile_rows`, its only remaining caller, so selected-table filtering stays local to the public loader.

### Functions intentionally kept

- `_coerce_rows` — required adapter for Spark DataFrames, Spark Rows, and list-like test fixtures.
- `_value` — required case-tolerant metadata field lookup for catalogue rows with mixed source casing.
- `_is_success` — required central success-status predicate for catalogue selection and profile-row loading.
- `_spark_types`, `_schema`, `_schema_field_names`, `_get_governance_metadata_schemas`, `_is_table_not_found_error`, and `_setup_governance_metadata_tables` — required bootstrap support used from notebook setup through `config.py`.
- `_catalogue_table_options` — required catalogue selection logic that picks the latest successful profile per logical table.
- `_build_column_context_records`, `_build_dq_rule_records`, and `_build_classification_records` — required record-building boundaries for the single backend commit action.
- `_json` — required normalization for optional AI suggestion and rule-parameter payloads.
- `_display_review_guidance` — intentionally shared by the three standalone review widgets to keep notebook behavior consistent without restoring the old combined widget.
