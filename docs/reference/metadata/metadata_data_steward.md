# METADATA_DATA_STEWARD

**Purpose:** Data steward person registry used by agreement intake; responsibility effective periods belong to METADATA_DATA_AGREEMENT.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 14 |
| Business columns | 6 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `steward_id` | `string` | [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md), `fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward`, `fabricops_kit.widgets.widget_render_data_steward._generate_steward_id` | Stable identifier for the steward row. |
| `steward_name` | `string` | [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md), `fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward` | Human-readable steward name. |
| `steward_role` | `string` | [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md), `fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward` | Configured steward role captured for the row. |
| `contact` | `string` | [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md), `fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward` | Contact detail captured for the steward record. |
| `is_active` | `boolean` | `fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward`, `fabricops_kit.widgets.shared.active_steward` | Whether the row is currently active. |
| `custom_fields_json` | `string` | `fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward`, `fabricops_kit.widgets.shared.serialize_custom_fields` | JSON payload stored for `custom_fields_json`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md)
