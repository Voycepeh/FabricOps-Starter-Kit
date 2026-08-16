# METADATA_DATA_AGREEMENT

Define why data can be shared, who is accountable, the approved purpose and usage, and the review period.

## Model

**Grain:** One version of one Data Agreement.

**Primary key:** `agreement_id` + `agreement_version`

**Relationships:**

* `provider_steward_id` → `METADATA_DATA_STEWARD.steward_id` (**N:1**). Each Data Agreement version has one provider steward; one steward can provide many agreement versions.
* `recipient_steward_id` → `METADATA_DATA_STEWARD.steward_id` (**N:1**). Each Data Agreement version has one recipient steward; one steward can receive many agreement versions.
* **1:N**: One Data Agreement lifecycle can govern many Data Contract rows through agreement_id.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 20 |
| Business columns | 12 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `agreement_id` | `string` | [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md), `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement`, `fabricops_kit.widgets.widget_render_data_agreement._generate_agreement_id` | Stable identifier for the agreement lifecycle. |
| `agreement_version` | `string` | `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement`, `fabricops_kit.widgets.widget_render_data_agreement._next_minor_version` | Canonical agreement version associated with the row. |
| `agreement_name` | `string` | [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md), `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement` | Human-readable name for the agreement. |
| `domain` | `string` | [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md), `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement` | Business domain recorded for the metadata row. |
| `provider_steward_id` | `string` | No traced writer in current agreement workflow | Steward identifier recorded for the provider side of the agreement. |
| `recipient_steward_id` | `string` | No traced writer in current agreement workflow | Steward identifier recorded for the recipient side of the agreement. |
| `start_date` | `date` | `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement`, `fabricops_kit.widgets.shared.parse_iso_date` | Date stored for `start_date`. |
| `expiry_date` | `date` | `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement`, `fabricops_kit.widgets.shared.parse_iso_date` | Date stored for `expiry_date`. |
| `business_purpose` | `string` | [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md), `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement` | Business purpose recorded for the agreement or access request. |
| `supporting_documents_json` | `string` | [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md), `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement` | JSON payload stored for `supporting_documents_json`. |
| `approved_usage_json` | `string` | [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md), `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement` | JSON payload stored for `approved_usage_json`. |
| `custom_fields_json` | `string` | `fabricops_kit.widgets.widget_render_data_agreement._create_or_update_data_agreement`, `fabricops_kit.widgets.shared.serialize_custom_fields` | JSON payload stored for `custom_fields_json`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

* [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md)
