# METADATA_ENRICHMENT_RULES

**Purpose:** Append-only enrichment and business metadata intent authored and reviewed through governance workflows.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `enrichment_rule_id` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `enrichment_rule_id`. |
| `enrichment_rule_version` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `enrichment_rule_version`. |
| `enrichment_rule_key` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `enrichment_rule_key`. |
| `metadata_table_key` | `string` | Yes | Enrichment and governance widgets | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | Yes | Enrichment and governance widgets | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `table_name` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `table_name`. |
| `column_name` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `column_name`. |
| `enrichment_scope` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `enrichment_scope`. |
| `enrichment_type` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `enrichment_type`. |
| `enrichment_payload_json` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `enrichment_payload_json`. |
| `business_name` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `business_name`. |
| `business_description` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `business_description`. |
| `business_meaning` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `business_meaning`. |
| `column_description` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `column_description`. |
| `classification` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `classification`. |
| `sensitivity_label` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `sensitivity_label`. |
| `pii_flag` | `boolean` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `pii_flag`. |
| `pii_type` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `pii_type`. |
| `data_domain` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `data_domain`. |
| `data_owner` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `data_owner`. |
| `data_steward` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `data_steward`. |
| `usage_notes` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `usage_notes`. |
| `quality_notes` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `quality_notes`. |
| `review_status` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `review_status`. |
| `review_state` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `review_state`. |
| `activation_state` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `activation_state`. |
| `is_active` | `boolean` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `is_active`. |
| `created_by_role` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `created_by_role`. |
| `source_notebook_type` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `source_notebook_type`. |
| `activation_reason` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `activation_reason`. |
| `activated_by` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `activated_by`. |
| `activated_at` | `timestamp` | Yes | Enrichment and governance widgets | Timestamp captured when a rule or enrichment record becomes active. |
| `requires_governance_review` | `boolean` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `requires_governance_review`. |
| `approval_policy` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `approval_policy`. |
| `governance_mode` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `governance_mode`. |
| `submitted_by` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `submitted_by`. |
| `submitted_at` | `timestamp` | Yes | Enrichment and governance widgets | Timestamp populated during a real submission into pending governance review. |
| `reviewed_by` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `reviewed_by`. |
| `reviewed_at` | `timestamp` | Yes | Enrichment and governance widgets | Timestamp captured when a governance reviewer records a review decision. |
| `review_decision` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `review_decision`. |
| `review_comment` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `review_comment`. |
| `bypass_reason` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `bypass_reason`. |
| `requires_post_review` | `boolean` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `requires_post_review`. |
| `supersedes_enrichment_rule_id` | `string` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `supersedes_enrichment_rule_id`. |
| `effective_from` | `date` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `effective_from`. |
| `effective_to` | `date` | Yes | Enrichment and governance widgets | Metadata Enrichment Rules field `effective_to`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
