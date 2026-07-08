# METADATA_GUARDRAIL_RULES

**Purpose:** Approved or pending schema, freshness, profile behavior, and DQ guardrail intent.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `rule_key` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `rule_key`. |
| `rule_id` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `rule_id`. |
| `metadata_column_key` | `string` | Yes | Guardrail authoring and governance widgets | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `metadata_table_key` | `string` | Yes | Guardrail authoring and governance widgets | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `environment_name`. |
| `dataset_name` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `dataset_name`. |
| `table_name` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `table_name`. |
| `column_name` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `column_name`. |
| `guardrail_type` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `guardrail_type`. |
| `rule_type` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `rule_type`. |
| `rule_parameters_json` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `rule_parameters_json`. |
| `severity` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `severity`. |
| `description` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `description`. |
| `activation_state` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `activation_state`. |
| `is_active` | `boolean` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `is_active`. |
| `review_status` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `review_status`. |
| `review_state` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `review_state`. |
| `created_by_role` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `created_by_role`. |
| `author_role` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `author_role`. |
| `suggestion_json` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `suggestion_json`. |
| `action_type` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `action_type`. |
| `source_notebook_type` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `source_notebook_type`. |
| `activation_reason` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `activation_reason`. |
| `activated_by` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `activated_by`. |
| `activated_at` | `timestamp` | Yes | Guardrail authoring and governance widgets | Timestamp captured when a rule or enrichment record becomes active. |
| `superseded_by_rule_key` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `superseded_by_rule_key`. |
| `notes` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `notes`. |
| `approval_required` | `boolean` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `approval_required`. |
| `approval_bypassed` | `boolean` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `approval_bypassed`. |
| `requires_governance_review` | `boolean` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `requires_governance_review`. |
| `requires_post_review` | `boolean` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `requires_post_review`. |
| `bypass_reason` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `bypass_reason`. |
| `bypassed_by` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `bypassed_by`. |
| `bypassed_at` | `timestamp` | Yes | Guardrail authoring and governance widgets | Timestamp captured when governance review is intentionally bypassed. |
| `governance_mode` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `governance_mode`. |
| `approval_policy` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `approval_policy`. |
| `submitted_by` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `submitted_by`. |
| `submitted_at` | `timestamp` | Yes | Guardrail authoring and governance widgets | Timestamp populated during a real submission into pending governance review. |
| `reviewed_by` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `reviewed_by`. |
| `reviewed_at` | `timestamp` | Yes | Guardrail authoring and governance widgets | Timestamp captured when a governance reviewer records a review decision. |
| `review_decision` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `review_decision`. |
| `review_comment` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `review_comment`. |
| `supersedes_rule_id` | `string` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `supersedes_rule_id`. |
| `effective_from` | `date` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `effective_from`. |
| `effective_to` | `date` | Yes | Guardrail authoring and governance widgets | Metadata Guardrail Rules field `effective_to`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_author_schema_freshness_profile_rules`](../../api/reference/widget_author_schema_freshness_profile_rules.md)
- [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
