# METADATA_ENRICHMENT

**Purpose:** Metadata Enrichment metadata table.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `enrichment_rule_id` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `enrichment_rule_id`. |
| `enrichment_rule_version` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `enrichment_rule_version`. |
| `enrichment_rule_key` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `enrichment_rule_key`. |
| `metadata_table_key` | `string` | Yes | FabricOps workflow | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | Yes | FabricOps workflow | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `table_name` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `table_name`. |
| `column_name` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `column_name`. |
| `enrichment_scope` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `enrichment_scope`. |
| `enrichment_type` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `enrichment_type`. |
| `enrichment_payload_json` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `enrichment_payload_json`. |
| `business_name` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `business_name`. |
| `business_description` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `business_description`. |
| `business_meaning` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `business_meaning`. |
| `column_description` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `column_description`. |
| `classification` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `classification`. |
| `sensitivity_label` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `sensitivity_label`. |
| `pii_flag` | `boolean` | Yes | FabricOps workflow | Metadata Enrichment field `pii_flag`. |
| `pii_type` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `pii_type`. |
| `data_domain` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `data_domain`. |
| `data_owner` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `data_owner`. |
| `data_steward` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `data_steward`. |
| `usage_notes` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `usage_notes`. |
| `quality_notes` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `quality_notes`. |
| `review_status` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `review_status`. |
| `review_state` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `review_state`. |
| `activation_state` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `activation_state`. |
| `is_active` | `boolean` | Yes | FabricOps workflow | Metadata Enrichment field `is_active`. |
| `created_by_role` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `created_by_role`. |
| `source_notebook_type` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `source_notebook_type`. |
| `activation_reason` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `activation_reason`. |
| `activated_by` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `activated_by`. |
| `activated_at` | `timestamp` | Yes | FabricOps workflow | Timestamp captured when a rule or enrichment record becomes active. |
| `requires_governance_review` | `boolean` | Yes | FabricOps workflow | Metadata Enrichment field `requires_governance_review`. |
| `approval_policy` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `approval_policy`. |
| `governance_mode` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `governance_mode`. |
| `submitted_by` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `submitted_by`. |
| `submitted_at` | `timestamp` | Yes | FabricOps workflow | Timestamp populated during a real submission into pending governance review. |
| `reviewed_by` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `reviewed_by`. |
| `reviewed_at` | `timestamp` | Yes | FabricOps workflow | Timestamp captured when a governance reviewer records a review decision. |
| `review_decision` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `review_decision`. |
| `review_comment` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `review_comment`. |
| `bypass_reason` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `bypass_reason`. |
| `requires_post_review` | `boolean` | Yes | FabricOps workflow | Metadata Enrichment field `requires_post_review`. |
| `supersedes_enrichment_rule_id` | `string` | Yes | FabricOps workflow | Metadata Enrichment field `supersedes_enrichment_rule_id`. |
| `effective_from` | `date` | Yes | FabricOps workflow | Metadata Enrichment field `effective_from`. |
| `effective_to` | `date` | Yes | FabricOps workflow | Metadata Enrichment field `effective_to`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |
