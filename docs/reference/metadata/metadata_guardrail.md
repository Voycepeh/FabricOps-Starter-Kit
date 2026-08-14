# METADATA_GUARDRAIL

**Purpose:** Append-only schema, freshness, profile-behavior, and DQ guardrail intent rows.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 55 |
| Business columns | 47 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `guardrail_rule_id` | `string` | `fabricops_kit.widgets.shared._base_guardrail_rule_record`, `fabricops_kit.widgets.shared._build_dq_rule_records` | Stable identifier for the guardrail rule row. |
| `configuration_version` | `integer` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Metadata Guardrail field `configuration_version`. |
| `rule_key` | `string` | `fabricops_kit.widgets.shared._base_guardrail_rule_record`, `fabricops_kit.widgets.shared._build_dq_rule_records`, `fabricops_kit.config.metadata_keys._build_dq_rule_key` | Stable key used to group lifecycle versions of the same guardrail or enrichment rule. |
| `rule_id` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Rule identity stored by the authoring workflow. |
| `metadata_column_key` | `string` | `fabricops_kit.widgets.shared._base_guardrail_rule_record`, `fabricops_kit.widgets.shared._build_dq_rule_records` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `metadata_table_key` | `string` | `fabricops_kit.widgets.shared._base_guardrail_rule_record`, `fabricops_kit.widgets.shared._build_dq_rule_records` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Environment name recorded for the metadata row. |
| `dataset_name` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Dataset name recorded for the metadata row. |
| `table_name` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Physical table name recorded for the metadata row. |
| `column_name` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Physical column name recorded for the metadata row. |
| `guardrail_type` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Guardrail family recorded for the row. |
| `rule_type` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Specific rule type recorded within the guardrail family. |
| `rule_parameters_json` | `string` | `fabricops_kit.widgets.shared._schema_freshness_profile_records_from_selection`, `fabricops_kit.widgets.shared._build_dq_rule_records` | Serialized rule parameters stored for the guardrail row. |
| `severity` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Severity recorded for the guardrail intent or result. |
| `description` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Human-readable description stored for the rule. |
| `activation_state` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Lifecycle activation state recorded for the row. |
| `is_active` | `boolean` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Whether the row is currently active. |
| `review_status` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Review status recorded for the row. |
| `review_state` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Review state recorded for the row. |
| `created_by_role` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Author role recorded for the row. |
| `author_role` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Detailed author role recorded for the guardrail row. |
| `suggestion_json` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Serialized suggested rule payload captured during authoring. |
| `action_type` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Authoring or governance action type recorded for the row. |
| `source_notebook_type` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Notebook type that authored or reviewed the row. |
| `activation_reason` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Human-readable reason for activating the row. |
| `activated_by` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Actor who activated the row. |
| `activated_at` | `timestamp` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Timestamp captured when a rule or enrichment record becomes active. |
| `superseded_by_rule_key` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Rule key that supersedes the current guardrail row. |
| `notes` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Free-text notes recorded for the row. |
| `approval_required` | `boolean` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Whether governance approval is required before activation. |
| `approval_bypassed` | `boolean` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Whether the row bypassed normal governance approval. |
| `requires_governance_review` | `boolean` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Whether the row still requires governance review. |
| `requires_post_review` | `boolean` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Whether the row requires review after immediate activation. |
| `bypass_reason` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Reason recorded when governance review was bypassed. |
| `bypassed_by` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Actor who bypassed governance review. |
| `bypassed_at` | `timestamp` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Timestamp captured when governance review is intentionally bypassed. |
| `governance_mode` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Governance mode recorded for the selected table. |
| `approval_policy` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Approval policy recorded for the selected table. |
| `submitted_by` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Actor who submitted the row for governance review. |
| `submitted_at` | `timestamp` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Timestamp populated during a real submission into pending governance review. |
| `reviewed_by` | `string` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Actor who recorded the governance review decision. |
| `reviewed_at` | `timestamp` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Timestamp captured when a governance reviewer records a review decision. |
| `review_decision` | `string` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Governance decision recorded for the row. |
| `review_comment` | `string` | [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), `fabricops_kit.widgets.shared.record_table_governance` | Reviewer comment recorded for the row. |
| `supersedes_rule_id` | `string` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Rule identifier superseded by the current row. |
| `effective_from` | `date` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Date when the record becomes effective. |
| `effective_to` | `date` | [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md) | Date when the record stops being effective. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md)
- [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
