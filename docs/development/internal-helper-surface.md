# Internal helper surface audit

This page records focused cleanup notes for helper-heavy modules. It is a maintainer handover aid. The public v1 callable API remains controlled by `src/fabricops_kit/__init__.py::__all__`.

## data_agreement.py

### Public v1 callables before

- `widget_select_agreement`
- `get_selected_agreement`
- `widget_render_agreement_evidence`
- `widget_render_data_steward`
- `widget_render_data_agreement`

### Public v1 callables after

- `widget_select_agreement`
- `get_selected_agreement`
- `widget_render_agreement_evidence`
- `widget_render_data_steward`
- `widget_render_data_agreement`

### Internal helper count before

- 66 underscore-prefixed helper functions before the first data-agreement cleanup.

### Internal helper count after

- 37 underscore-prefixed helper functions after the follow-up data-agreement cleanup.

### Deleted helpers

- `_agreement_dropdown_options`
- `_agreement_version_options`
- `_build_steward_dropdown_options`
- `_get_data_agreement_evidence_schema`
- `_get_data_agreement_schema`
- `_get_data_steward_schema`
- `_get_standard_runtime_audit_columns`
- `_load_active_data_steward_profiles`
- `_resolve_agreement_identity`
- `_widget_render_agreement_intake_app`
- `_default_dropdown_value`
- `_field_label`
- `_notebookutils_file_size`
- `_notebookutils_fs_exists`
- `_option_values`
- `_parse_evidence_file_paths`
- `_set_widget_value`
- `_steward_role_options`
- `_table_name`
- `_validate_evidence_file_path`
- `_widget_config`
- `_widget_field_value`

### Merged helpers

- `_evidence_file_name_from_path`, `_parse_evidence_file_paths`, `_validate_evidence_file_path`, `_notebookutils_fs_exists`, and `_notebookutils_file_size` were merged into `_prepare_evidence_file_references` so parsing, validation, optional existence checks, MIME lookup, and file-size lookup stay in one evidence-preparation flow.
- `_load_agreements` was merged into `widget_select_agreement`, preserving the configured-read error message without a single-use wrapper.
- `_steward_active_value` was merged into `_create_or_update_data_steward`, where saved active-state derivation is easiest to trace.
- `_widget_layout` was merged into `_widget_common`, keeping shared widget layout defaults in one helper.
- `_table_name`, `_steward_role_options`, and `_widget_config` were replaced by direct `_config_value` use where table names, role options, or widget defaults are needed.

### Inlined helpers

- `_column_names` was inlined in metadata table validation.
- `_row_search_text` was inlined in `_render_searchable_selector` while building indexed selector rows.
- `_selector_context_html` was inlined in `_render_searchable_selector` so selector context rendering stays next to selector state updates.
- `_default_dropdown_value`, `_option_values`, `_field_label`, `_set_widget_value`, and `_widget_field_value` were inlined or localized inside selector and form rendering where the value-shaping behavior is used.

### Helpers intentionally kept

- Optional dependency and widget primitives: `_require_ipywidgets`, `_widget_common`, `_standard_widget`, `_html_escape`, `_render_searchable_selector`, `_render_custom_fields`, `_collect_custom_fields`, `_agreement_identity_text`.
- Config and schema routing: `_config_value`, `_get_widget_visible_fields`, `_ensure_metadata_tables`, `_setup_data_agreement_tables`.
- Row normalization and validation: `_coerce_row_dicts`, `_to_bool`, `_parse_iso_date`, `_parse_contract_version`, `_next_minor_version`, `_to_iso_date`, `_active_steward`.
- Steward and agreement persistence: `_latest_by_key`, `_generate_steward_id`, `_list_data_stewards`, `_write_row`, `_create_or_update_data_steward`, `_latest_agreement_versions`, `_list_all_data_agreement_rows`, `_list_data_agreements`, `_generate_agreement_id`, `_business_agreement_snapshot`, `_create_or_update_data_agreement`.
- Evidence persistence: `_get_notebookutils`, `_prepare_evidence_file_references`, `_save_agreement_evidence_records`.
- Widget assembly: `_render_maintenance_widget`, `_render_agreement_evidence_widget`.

### Notes for future maintainers

The cleanup removes the obsolete combined-widget implementation and strips out compatibility/documentation-only helpers that are not part of the v1 public contract. Keep the current boundaries around metadata routing, validation, persistence, reusable widget rendering, agreement selection, and evidence preparation. Avoid reintroducing wrapper-only helpers unless they support reuse across multiple public widget flows.

## governance_review.py

### Public v1 callables before

- `widget_select_catalogue_table`
- `get_selected_catalogue_table`
- `load_catalogue_profile_rows`
- `widget_review_column_context`
- `widget_review_dq_rules`
- `widget_review_column_classification`
- `record_table_governance`

### Public v1 callables after

- `widget_select_catalogue_table`
- `get_selected_catalogue_table`
- `load_catalogue_profile_rows`
- `widget_review_column_context`
- `widget_review_dq_rules`
- `widget_review_column_classification`
- `record_table_governance`

### Internal helper count before

- 24 underscore-prefixed helper functions.

### Internal helper count after

- 15 underscore-prefixed helper functions.

### Deleted helpers

- `_build_profile_summary` — dead display-only summary helper with no notebook or package callers.
- `_latest_by_column` — legacy latest-approved-state helper tied to earlier combined review flows.
- `_optional_ai_generate_response` — dead Fabric AI wrapper not used by the standalone v1 review widgets.
- `_widget_review_table_governance` — obsolete combined-widget implementation that must not return as public v1 API.

### Merged helpers

- `_commit_column_context`, `_commit_dq_rules`, and `_commit_column_classification` were merged into the consolidated backend commit loop in `record_table_governance`.

### Inlined helpers

- `_audit` was inlined into the row builders by calling `_build_runtime_audit_fields` directly when commit metadata is available.
- `_row_metadata_table_key` was inlined into `load_catalogue_profile_rows`, its only remaining caller, so selected-table filtering stays local to the public loader.

### Helpers intentionally kept

- `_coerce_rows` — required adapter for Spark DataFrames, Spark Rows, and list-like test fixtures.
- `_value` — required case-tolerant metadata field lookup for catalogue rows with mixed source casing.
- `_is_success` — required central success-status predicate for catalogue selection and profile-row loading.
- `_spark_types`, `_schema`, `_schema_field_names`, `_get_governance_metadata_schemas`, `_is_table_not_found_error`, and `_setup_governance_metadata_tables` — required bootstrap support used from notebook setup through `config.py`.
- `_catalogue_table_options` — required catalogue selection logic that picks the latest successful profile per logical table.
- `_build_column_context_records`, `_build_dq_rule_records`, and `_build_classification_records` — required record-building boundaries for the single backend commit action.
- `_json` — required normalization for optional AI suggestion and rule-parameter payloads.
- `_display_review_guidance` — intentionally shared by the three standalone review widgets to keep notebook behavior consistent without restoring the old combined widget.

### Notes for future maintainers

The public governance-review flow is intentionally split into standalone review widgets plus one backend commit function. Do not restore the retired combined review widget or wrapper-only commit helpers. Keep metadata setup helpers available because notebook setup still reaches them indirectly through `config.py`.

## drift.py

### Public v1 callables before

- `validate_schema`
- `monitor_data_changes`
- `stop_if_failed`

### Public v1 callables after

- `validate_schema`
- `monitor_data_changes`
- `stop_if_failed`

### Internal helper count before

- 41 underscore-prefixed helper functions.

### Internal helper count after

- 14 underscore-prefixed helper functions.

### Deleted helpers

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

### Merged helpers

- `_default_profile_drift_policy` was replaced with `_DEFAULT_PROFILE_DRIFT_POLICY` so direct profile-drift checks and data-change presets share a simple threshold constant instead of a function wrapper.
- `_normalize_baseline_mode` was merged into `_load_latest_profile`, where baseline mode validation is used.
- `_as_monitor_only_result` was merged into `monitor_data_changes`, keeping monitor-only behavior next to preset resolution and the final guardrail result shape.

### Inlined helpers

- `_check_schema` was inlined into `validate_schema`, leaving schema enforcement in one public guardrail entrypoint while preserving expected-schema, preset, and datatype comparison behavior.
- `_profile_check_status` was inlined into numeric PSI and categorical-distance checks because it only encoded a two-threshold status decision at the call sites.
- `_assert_no_blocking_profile_drift` was removed in favor of `stop_if_failed`, which remains the single public stop mechanism for guardrail result objects.

### Helpers intentionally kept

- `_normalize_datatype` — preserves Spark/pandas datatype alias handling for schema validation.
- `_actual_schema` — isolates Spark/pandas/dataframe-like schema extraction.
- `_row_get` — normalizes dictionary, Spark Row, and object-style metadata row access.
- `_parse_distribution` — safely parses JSON distribution payloads from profile metadata.
- `_normalize_profile` — keeps profile dictionaries, Spark DataFrames, and collected rows in one comparison shape.
- `_extract_numeric_distribution_bin_edges` — reuses baseline numeric bins so current profiles remain comparable.
- `_extract_categorical_distribution_categories` — reuses baseline categories so categorical comparisons can identify new categories.
- `_proportions` — supports PSI calculation with zero-count protection.
- `_numeric_psi` — implements numeric distribution drift scoring.
- `_categorical_distance` — implements categorical distribution drift scoring and new-category reporting.
- `_check_profile_drift` — compares normalized profiles against row-count, null, distinct, PSI, and categorical thresholds.
- `_is_missing_table_error` — treats missing metadata tables as no-baseline rather than runtime failures.
- `_load_latest_profile` — selects latest successful or approved profile baselines from metadata.
- `_data_change_preset_config` — validates presets and threshold overrides while preserving user configurability.

### Notes for future maintainers

`UnsupportedDataFrameEngineError` and `IncrementalSafetyError` remain import-compatible for previously documented internal imports, but the removed engine-detection and incremental-safety helper paths were not restored. Keep drift guardrails focused on schema validation, profile-drift monitoring, and `stop_if_failed`; avoid rebuilding unused partition or incremental-safety flows unless they become explicit public requirements.
