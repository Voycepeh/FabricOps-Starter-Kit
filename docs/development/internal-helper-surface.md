# Internal helper surface inventory

This development note tracks modules where the public v1 callable surface is intentionally much smaller than the implementation surface. Keep this document focused on cleanup decisions that help future contributors understand why helpers were kept, merged, inlined, or deleted.

## `src/fabricops_kit/data_agreement.py`

| Metric | Count |
|---|---:|
| Public v1 callables | 5 |
| Internal helper count before this cleanup | 66 |
| Internal helper count after this cleanup | 49 |

Public v1 callables preserved:

- `widget_render_data_steward`
- `widget_render_data_agreement`
- `widget_render_agreement_evidence`
- `widget_select_agreement`
- `get_selected_agreement`

### Functions deleted

These helpers were removed because they were dead, docs-only, compatibility-only, or tied to the retired combined intake app:

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

### Functions merged

These helpers had useful behavior but did not need their own callable boundary:

- `_evidence_file_name_from_path` was merged into evidence path validation and optional file-size lookup.
- `_load_agreements` was merged into `widget_select_agreement`, keeping the same configured-read error message without a single-use wrapper.
- `_steward_active_value` was merged into `_create_or_update_data_steward`, where saved active-state derivation is easiest to trace.
- `_widget_layout` was merged into `_widget_common`, keeping all shared widget layout defaults in one helper.

### Functions inlined

These single-use helpers were inlined at their only call sites:

- `_column_names` was inlined in metadata table validation.
- `_row_search_text` was inlined in `_render_searchable_selector` while building indexed selector rows.
- `_selector_context_html` was inlined in `_render_searchable_selector` so selector context rendering stays next to selector state updates.

### Functions intentionally kept

The remaining helpers keep a real responsibility boundary:

- Optional dependency and widget primitives: `_require_ipywidgets`, `_widget_common`, `_standard_widget`, `_set_widget_value`, `_widget_field_value`, `_default_dropdown_value`, `_option_values`, `_html_escape`, `_field_label`, `_render_searchable_selector`, `_render_custom_fields`, `_collect_custom_fields`, `_agreement_identity_text`.
- Config/schema routing: `_config_value`, `_table_name`, `_steward_role_options`, `_widget_config`, `_get_widget_visible_fields`, `_ensure_metadata_tables`, `_setup_data_agreement_tables`.
- Row normalization and validation: `_coerce_row_dicts`, `_to_bool`, `_parse_iso_date`, `_parse_contract_version`, `_next_minor_version`, `_to_iso_date`, `_active_steward`.
- Steward and agreement persistence: `_latest_by_key`, `_generate_steward_id`, `_list_data_stewards`, `_write_row`, `_create_or_update_data_steward`, `_latest_agreement_versions`, `_list_all_data_agreement_rows`, `_list_data_agreements`, `_generate_agreement_id`, `_business_agreement_snapshot`, `_create_or_update_data_agreement`.
- Evidence persistence: `_parse_evidence_file_paths`, `_validate_evidence_file_path`, `_get_notebookutils`, `_notebookutils_fs_exists`, `_notebookutils_file_size`, `_prepare_evidence_file_references`, `_save_agreement_evidence_records`.
- Widget assembly: `_render_maintenance_widget`, `_render_agreement_evidence_widget`.

### Cleanup rationale

The cleanup removes the obsolete combined-widget implementation and strips out compatibility/documentation-only helpers that are not part of the v1 public contract. The remaining implementation keeps clear boundaries for metadata routing, validation, persistence, reusable widget rendering, and agreement selection without preserving wrapper chains for internal backward compatibility.
