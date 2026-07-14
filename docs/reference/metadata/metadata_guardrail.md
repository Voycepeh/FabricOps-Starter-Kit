# METADATA_GUARDRAIL

**Purpose:** Metadata Guardrail metadata table.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `guardrail_rule_id` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `guardrail_rule_id`. |
| `rule_key` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `rule_key`. |
| `rule_id` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `rule_id`. |
| `metadata_column_key` | `string` | Yes | FabricOps workflow | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `metadata_table_key` | `string` | Yes | FabricOps workflow | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `environment_name`. |
| `dataset_name` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `dataset_name`. |
| `table_name` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `table_name`. |
| `column_name` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `column_name`. |
| `guardrail_type` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `guardrail_type`. |
| `rule_type` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `rule_type`. |
| `rule_parameters_json` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `rule_parameters_json`. |
| `severity` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `severity`. |
| `description` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `description`. |
| `activation_state` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `activation_state`. |
| `is_active` | `boolean` | Yes | FabricOps workflow | Metadata Guardrail field `is_active`. |
| `review_status` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `review_status`. |
| `review_state` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `review_state`. |
| `created_by_role` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `created_by_role`. |
| `author_role` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `author_role`. |
| `suggestion_json` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `suggestion_json`. |
| `action_type` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `action_type`. |
| `source_notebook_type` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `source_notebook_type`. |
| `activation_reason` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `activation_reason`. |
| `activated_by` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `activated_by`. |
| `activated_at` | `timestamp` | Yes | FabricOps workflow | Timestamp captured when a rule or enrichment record becomes active. |
| `superseded_by_rule_key` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `superseded_by_rule_key`. |
| `notes` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `notes`. |
| `approval_required` | `boolean` | Yes | FabricOps workflow | Metadata Guardrail field `approval_required`. |
| `approval_bypassed` | `boolean` | Yes | FabricOps workflow | Metadata Guardrail field `approval_bypassed`. |
| `requires_governance_review` | `boolean` | Yes | FabricOps workflow | Metadata Guardrail field `requires_governance_review`. |
| `requires_post_review` | `boolean` | Yes | FabricOps workflow | Metadata Guardrail field `requires_post_review`. |
| `bypass_reason` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `bypass_reason`. |
| `bypassed_by` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `bypassed_by`. |
| `bypassed_at` | `timestamp` | Yes | FabricOps workflow | Timestamp captured when governance review is intentionally bypassed. |
| `governance_mode` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `governance_mode`. |
| `approval_policy` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `approval_policy`. |
| `submitted_by` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `submitted_by`. |
| `submitted_at` | `timestamp` | Yes | FabricOps workflow | Timestamp populated during a real submission into pending governance review. |
| `reviewed_by` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `reviewed_by`. |
| `reviewed_at` | `timestamp` | Yes | FabricOps workflow | Timestamp captured when a governance reviewer records a review decision. |
| `review_decision` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `review_decision`. |
| `review_comment` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `review_comment`. |
| `supersedes_rule_id` | `string` | Yes | FabricOps workflow | Metadata Guardrail field `supersedes_rule_id`. |
| `effective_from` | `date` | Yes | FabricOps workflow | Metadata Guardrail field `effective_from`. |
| `effective_to` | `date` | Yes | FabricOps workflow | Metadata Guardrail field `effective_to`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |
