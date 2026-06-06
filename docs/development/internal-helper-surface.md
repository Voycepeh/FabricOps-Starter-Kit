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
