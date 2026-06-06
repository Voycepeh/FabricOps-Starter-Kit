# v1 callable surface inventory

## Summary

- Before callable count: **71** exported callable functions across essential and optional categories.
- After callable count: **26** curated v1 template callables.
- Definition: a callable is a function that a notebook template user actively calls in a template cell.
- Source of truth: `src/fabricops_kit/__init__.py::__all__`, enforced by `tests/contract/test_public_contract.py` and mirrored in `scripts/generate_function_reference.py::V1_CALLABLES`.

## Final v1 callable list

1. `setup_notebook`
2. `setup_data_agreement_tables`
3. `setup_notebook_registry_table`
4. `setup_governance_metadata_tables`
5. `widget_render_agreement_intake_app`
6. `widget_select_agreement`
7. `get_selected_agreement`
8. `read_lakehouse_table`
9. `write_lakehouse_table`
10. `read_lakehouse_csv`
11. `read_lakehouse_parquet`
12. `read_lakehouse_excel`
13. `read_warehouse_table`
14. `write_warehouse_table`
15. `profile_dataframe`
16. `validate_schema`
17. `monitor_data_changes`
18. `stop_if_failed`
19. `build_lineage_records`
20. `build_handover`
21. `render_handover_markdown`
22. `widget_select_catalogue_table`
23. `get_selected_catalogue_table`
24. `load_catalogue_profile_rows`
25. `widget_review_table_governance`
26. `record_table_governance`

## Deleted from the public callable surface

The following previous public/exported functions were removed from the v1 callable surface and are no longer importable from the package root:

- Business context drafting/review helpers: `draft_business_context`, `prepare_business_context_profile_input`, `extract_column_business_context_suggestions`, `widget_review_business_context`, `get_reviewed_business_context_rows`, `write_business_context`.
- DQ drafting/review/enforcement aliases: `draft_dq_rules`, `widget_review_dq_rules`, `get_dq_review_results`, `write_dq_rules`, `load_dq_rules`, `enforce_dq`, `assert_dq_passed`, `validate_dq_rules`, `widget_review_dq_rule_deactivations`.
- Governance drafting/review aliases: `draft_governance`, `prepare_governance_input`, `extract_governance_suggestions`, `widget_review_governance`, `write_governance`, `load_governance`.
- Low-level metadata and registry helpers: `register_current_notebook`, `load_notebook_registry`, `get_notebook_registry_schema`, `build_runtime_audit_fields`, `current_notebook_active_registrations`.
- Version/banner helpers: `get_package_version`, `get_docs_version`, `get_docs_url`, `get_release_notes_url`, `print_runtime_banner`.
- Advanced drift/incremental helpers: `check_partition_drift`, `build_and_write_partition_snapshot`, `load_latest_partition_snapshot`, `summarize_drift_results`, `build_drift_evidence_record`, `prepare_drift_baselines`, `default_incremental_safety_policy`, `build_partition_snapshot`, `compare_partition_snapshots`, `assert_incremental_safe`, `build_incremental_safety_records`.
- Row/key builders and one-step commit helpers: `build_evidence_row`, `build_metadata_table_key`, `build_metadata_column_key`, `build_dq_rule_key`, `build_profile_summary`, `latest_by_column`, `build_column_context_records`, `build_dq_rule_records`, `build_classification_records`, `commit_column_context`, `commit_dq_rules`, `commit_column_classification`.
- Optional/internal utilities: `catalogue_table_options`, `get_governance_metadata_schemas`, `optional_ai_generate_response`, `default_evidence_types`, `normalise_records_by_column`, `column_context_rows_for_spark`, `write_metadata_rows`, `detect_dataframe_engine`, `check_naming_convention`, `seed_minimal_sample_source_table`, `load_dataset_contract`, `validate_dataset_contract`, `assert_valid_dataset_contract`, `load_and_validate_dataset_contract`, `build_lineage_handover_markdown`, `build_handover_record`.

## Merged functions

- `build_column_context_records` + `commit_column_context` merged into `record_table_governance`.
- `build_dq_rule_records` + `commit_dq_rules` merged into `record_table_governance`.
- `build_classification_records` + `commit_column_classification` merged into `record_table_governance`.
- Separate agreement-maintenance widgets are superseded in templates by `widget_render_agreement_intake_app`.

## Renamed/private functions

Non-v1 helpers that are still needed internally now use leading-underscore names in source modules. Examples include `_build_runtime_audit_fields`, `_get_governance_metadata_schemas`, `_build_column_context_records`, `_commit_dq_rules`, `_print_runtime_banner`, and `_validate_dq_rules`.

## Deleted modules

None. Existing modules remain because they still contain internal implementation used by the v1 workflow or preserve module organization for future source maintenance.

## Rationale

The v1 surface keeps one high-level function per notebook user action: configure the environment, create/select agreements, read/write governed Fabric data, profile data, validate schema, monitor drift, capture lineage/handover evidence, and record approved table governance. Low-level coercion, key generation, row building, Spark conversion, docs metadata, and compatibility aliases are internal implementation details rather than notebook-template callables.
