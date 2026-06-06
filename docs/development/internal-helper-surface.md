# Internal helper surface inventory

This development note tracks modules where the public v1 callable surface is intentionally much smaller than the implementation surface. Keep this document focused on cleanup decisions that help future contributors understand why helpers were kept, merged, inlined, or deleted.

## `src/fabricops_kit/data_agreement.py`

| Metric | Count |
|---|---:|
| Public v1 callables | 5 |
| Internal helper count before first cleanup | 66 |
| Internal helper count after first cleanup | 49 |
| Internal helper count after follow-up cleanup | 37 |

Public v1 callables preserved:

- `widget_render_data_steward`
- `widget_render_data_agreement`
- `widget_render_agreement_evidence`
- `widget_select_agreement`
- `get_selected_agreement`

### Functions deleted

These helpers were removed because they were dead, docs-only, compatibility-only, tied to the retired combined intake app, or small wrappers better handled inside their owning flow:

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

### Functions merged

These helpers had useful behavior but did not need their own callable boundary:

- `_evidence_file_name_from_path`, `_parse_evidence_file_paths`, `_validate_evidence_file_path`, `_notebookutils_fs_exists`, and `_notebookutils_file_size` were merged into `_prepare_evidence_file_references` so parsing, validation, optional existence checks, MIME lookup, and file-size lookup live in one evidence-preparation flow.
- `_load_agreements` was merged into `widget_select_agreement`, keeping the same configured-read error message without a single-use wrapper.
- `_steward_active_value` was merged into `_create_or_update_data_steward`, where saved active-state derivation is easiest to trace.
- `_widget_layout` was merged into `_widget_common`, keeping all shared widget layout defaults in one helper.
- `_table_name`, `_steward_role_options`, and `_widget_config` were replaced by direct `_config_value` use at the point where table names, role options, or widget defaults are needed.

### Functions inlined

These single-use helpers were inlined at their only call sites:

- `_column_names` was inlined in metadata table validation.
- `_row_search_text` was inlined in `_render_searchable_selector` while building indexed selector rows.
- `_selector_context_html` was inlined in `_render_searchable_selector` so selector context rendering stays next to selector state updates.
- `_default_dropdown_value`, `_option_values`, `_field_label`, `_set_widget_value`, and `_widget_field_value` were inlined or localized inside selector/form rendering where the value-shaping behavior is used.

### Functions intentionally kept

The remaining helpers keep a real responsibility boundary:

- Optional dependency and widget primitives: `_require_ipywidgets`, `_widget_common`, `_standard_widget`, `_html_escape`, `_render_searchable_selector`, `_render_custom_fields`, `_collect_custom_fields`, `_agreement_identity_text`.
- Config/schema routing: `_config_value`, `_get_widget_visible_fields`, `_ensure_metadata_tables`, `_setup_data_agreement_tables`.
- Row normalization and validation: `_coerce_row_dicts`, `_to_bool`, `_parse_iso_date`, `_parse_contract_version`, `_next_minor_version`, `_to_iso_date`, `_active_steward`.
- Steward and agreement persistence: `_latest_by_key`, `_generate_steward_id`, `_list_data_stewards`, `_write_row`, `_create_or_update_data_steward`, `_latest_agreement_versions`, `_list_all_data_agreement_rows`, `_list_data_agreements`, `_generate_agreement_id`, `_business_agreement_snapshot`, `_create_or_update_data_agreement`.
- Evidence persistence: `_get_notebookutils`, `_prepare_evidence_file_references`, `_save_agreement_evidence_records`.
- Widget assembly: `_render_maintenance_widget`, `_render_agreement_evidence_widget`.

### Cleanup rationale

The cleanup removes the obsolete combined-widget implementation and strips out compatibility/documentation-only helpers that are not part of the v1 public contract. The follow-up cleanup consolidates config access, dropdown value handling, form value shaping, and evidence path preparation while preserving the core boundaries for metadata routing, validation, persistence, reusable widget rendering, and agreement selection.
