# METADATA_ENRICHMENT

**Purpose:** Append-only enrichment intent and approved business context for governed tables and columns.

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `enrichment_rule_id` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Stable identifier for the enrichment rule row. |
| `enrichment_rule_version` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Version recorded for the enrichment rule row. |
| `enrichment_rule_key` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.config.metadata_keys._build_dq_rule_key` | Stable key used to group lifecycle versions of the same enrichment rule. |
| `metadata_table_key` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._approved_column_identity` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._approved_column_identity` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `table_name` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Physical table name recorded for the metadata row. |
| `column_name` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Physical column name recorded for the metadata row. |
| `enrichment_scope` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Whether the enrichment row applies to a table or column. |
| `enrichment_type` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Enrichment type recorded for the row. |
| `enrichment_payload_json` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Serialized enrichment payload stored for the row. |
| `business_name` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Business-friendly name recorded for the table or column. |
| `business_description` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Business description recorded for the table or column. |
| `business_meaning` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Business meaning recorded for the table or column. |
| `column_description` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Column description recorded by the enrichment workflow. |
| `classification` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Classification recorded for the table or column. |
| `sensitivity_label` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Sensitivity label recorded for the table or column. |
| `pii_flag` | `boolean` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Whether the table or column is marked as containing PII. |
| `pii_type` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | PII type recorded for the table or column. |
| `data_domain` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Business data domain recorded for the row. |
| `data_owner` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Business owner recorded for the row. |
| `data_steward` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Business steward recorded for the row. |
| `usage_notes` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Usage notes recorded for the row. |
| `quality_notes` | `string` | `fabricops_kit.widgets.shared.build_enrichment_rule_records`, `fabricops_kit.widgets.shared._enrichment_payload_from_review` | Quality notes recorded for the row. |
| `review_status` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Review status recorded for the row. |
| `review_state` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Review state recorded for the row. |
| `activation_state` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Lifecycle activation state recorded for the row. |
| `is_active` | `boolean` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Whether the row is currently active. |
| `created_by_role` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Author role recorded for the row. |
| `source_notebook_type` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Notebook type that authored or reviewed the row. |
| `activation_reason` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Human-readable reason for activating the row. |
| `activated_by` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Actor who activated the row. |
| `activated_at` | `timestamp` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Timestamp captured when a rule or enrichment record becomes active. |
| `requires_governance_review` | `boolean` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Whether the row still requires governance review. |
| `approval_policy` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Approval policy recorded for the selected table. |
| `governance_mode` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Governance mode recorded for the selected table. |
| `submitted_by` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Actor who submitted the row for governance review. |
| `submitted_at` | `timestamp` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Timestamp populated during a real submission into pending governance review. |
| `reviewed_by` | `string` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Actor who recorded the governance review decision. |
| `reviewed_at` | `timestamp` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Timestamp captured when a governance reviewer records a review decision. |
| `review_decision` | `string` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Governance decision recorded for the row. |
| `review_comment` | `string` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Reviewer comment recorded for the row. |
| `bypass_reason` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Reason recorded when governance review was bypassed. |
| `requires_post_review` | `boolean` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Whether the row requires review after immediate activation. |
| `supersedes_enrichment_rule_id` | `string` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Enrichment rule identifier superseded by the current row. |
| `effective_from` | `date` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Date when the record becomes effective. |
| `effective_to` | `date` | [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), `fabricops_kit.widgets.shared.build_enrichment_rule_records` | Date when the record stops being effective. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
