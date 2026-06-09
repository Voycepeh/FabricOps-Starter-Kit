# v1 callable surface inventory

## Summary

- Before callable count: **71** exported callable functions across essential and optional categories.
- Revised after callable count: **30** curated v1 template callables.
- Definition: a callable is a function that a notebook template user actively calls in a template cell.
- Source of truth: `src/fabricops_kit/__init__.py::__all__`, enforced by `tests/contract/test_public_contract.py` and mirrored in `scripts/generate_function_reference.py::V1_CALLABLES`.

## Final v1 callable list

1. `setup_notebook`
2. `setup_metadata_tables`
3. `widget_render_data_steward`
4. `widget_render_data_agreement`
5. `widget_render_agreement_evidence`
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
17. `enforce_catalogue_stability`
18. `stop_if_failed`
19. `enforce_dq_rules`
20. `build_lineage_records`
21. `write_catalogue_evidence`
22. `write_pipeline_lineage`
23. `write_pipeline_run_summary`
24. `widget_select_catalogue_table`
25. `get_selected_catalogue_table`
26. `load_catalogue_profile_rows`
27. `widget_review_column_context`
28. `widget_review_dq_rules`
29. `widget_review_column_classification`
30. `record_table_governance`

## Deleted from the public callable surface

The following previous public/exported functions were removed from the v1 callable surface and are no longer importable from the package root:

- Specific metadata setup helpers: `setup_data_agreement_tables`, `setup_notebook_registry_table`, `setup_governance_metadata_tables`.
- Combined/large Fabric widgets: `widget_render_agreement_intake_app`, `widget_review_table_governance`.
- Business context drafting/review helpers: `draft_business_context`, `prepare_business_context_profile_input`, `extract_column_business_context_suggestions`, `widget_review_business_context`, `get_reviewed_business_context_rows`, `write_business_context`.
- DQ drafting/review/enforcement aliases: `draft_dq_rules`, `get_dq_review_results`, `write_dq_rules`, `load_dq_rules`, `enforce_dq`, `assert_dq_passed`, `validate_dq_rules`, `widget_review_dq_rule_deactivations`.
- Governance drafting/review aliases: `draft_governance`, `prepare_governance_input`, `extract_governance_suggestions`, `widget_review_governance`, `write_governance`, `load_governance`.
- Low-level metadata and registry helpers: `register_current_notebook`, `load_notebook_registry`, `get_notebook_registry_schema`, `build_runtime_audit_fields`, `current_notebook_active_registrations`.
- Version/banner helpers: `get_package_version`, `get_docs_version`, `get_docs_url`, `get_release_notes_url`, `print_runtime_banner`.
- Advanced incremental/profile comparison helpers and low-level row/key builders: `build_and_write_partition_snapshot`, `load_latest_partition_snapshot`, `default_incremental_safety_policy`, `build_partition_snapshot`, `assert_incremental_safe`, `build_incremental_safety_records`, `build_evidence_row`, `build_metadata_table_key`, `build_metadata_column_key`, `build_dq_rule_key`, `build_profile_summary`, `latest_by_column`, `build_column_context_records`, `build_dq_rule_records`, `build_classification_records`, `commit_column_context`, `commit_dq_rules`, `commit_column_classification`.
- Optional/internal utilities: `catalogue_table_options`, `get_governance_metadata_schemas`, `optional_ai_generate_response`, `default_evidence_types`, `normalise_records_by_column`, `column_context_rows_for_spark`, `write_metadata_rows`, `detect_dataframe_engine`, `check_naming_convention`, `seed_minimal_sample_source_table`, `load_dataset_contract`, `validate_dataset_contract`, `assert_valid_dataset_contract`, and `load_and_validate_dataset_contract`.

## Added pipeline evidence helpers

`02_pipeline` continues to use existing public read, profiling, guardrail, DQ, and write helpers directly. The added public pipeline helpers are limited to noisy metadata evidence tasks: catalogue evidence enrichment, many-to-many lineage persistence, and runtime summary logging.

## Merged functions

- `setup_data_agreement_tables`, `setup_notebook_registry_table`, and `setup_governance_metadata_tables` folded into `setup_metadata_tables` so `00_env_config` has one metadata setup action.
- `build_column_context_records` + `commit_column_context` merged into `record_table_governance`.
- `build_dq_rule_records` + `commit_dq_rules` merged into `record_table_governance`.
- `build_classification_records` + `commit_column_classification` merged into `record_table_governance`.

## Restored standalone widgets

The standalone agreement widgets `widget_render_data_steward`, `widget_render_data_agreement`, and `widget_render_agreement_evidence` are v1 callables because large combined widgets are fragile in Microsoft Fabric notebooks. The standalone governance review widgets `widget_review_column_context`, `widget_review_dq_rules`, and `widget_review_column_classification` are also public for the same reason.

## Renamed/private functions

Non-v1 helpers that are still needed internally now use leading-underscore names in source modules. Examples include `_setup_data_agreement_tables`, `_setup_notebook_registry_table`, `_setup_governance_metadata_tables`, `_widget_review_table_governance`, `_build_runtime_audit_fields`, `_get_governance_metadata_schemas`, `_build_column_context_records`, `_commit_dq_rules`, `_print_runtime_banner`, and `_validate_dq_rules`.

## 03_governance wrapper rationale

`get_selected_catalogue_table` remains public because users must explicitly read the stable table identity after interacting with `widget_select_catalogue_table`. It accepts the selector returned by the widget for readability while preserving widget state fallback.

`load_catalogue_profile_rows` remains public because it expresses the v1 action "load profile rows for the selected catalogue table". It is more than a pass-through read: it routes to the configured metadata lakehouse, filters to the selected environment/dataset/table/profile run/stage/key, requires successful profile evidence, and fails fast when no selected profile rows exist.

## Deleted modules

The obsolete `handover`, `business_context`, `data_governance`, `data_quality`, `versioning`, and `_utils` modules are not active v1 implementation modules. Their remaining behavior is either folded into active modules or intentionally absent from the public v1 surface.

## Rationale

The v1 surface keeps one high-level function per backend user action while preserving smaller standalone widget cells for Fabric stability. Notebook users configure schemas and stability settings directly in templates, call `validate_schema` and `enforce_catalogue_stability`, and use `stop_if_failed` only to stop on those guardrail result objects. Low-level coercion, key generation, row building, Spark conversion, docs metadata, and non-template helpers are internal implementation details rather than notebook-template callables.
