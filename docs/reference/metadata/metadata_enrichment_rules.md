# METADATA_ENRICHMENT_RULES

**Purpose:** Append-only enrichment and business metadata intent authored and reviewed through governance workflows.

## Starter Kit usage

- **Written by notebook/template:** 02_pipeline.ipynb, 03_governance.ipynb
- **Written by function or widget:** [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md), [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- **Read by function or widget:** [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- **Related template step:** 02_pipeline.ipynb, 03_governance.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `enrichment_rule_id` | `string` | Nullable |
| `enrichment_rule_version` | `string` | Nullable |
| `enrichment_rule_key` | `string` | Nullable |
| `metadata_table_key` | `string` | Nullable |
| `metadata_column_key` | `string` | Nullable |
| `table_name` | `string` | Nullable |
| `column_name` | `string` | Nullable |
| `enrichment_scope` | `string` | Nullable |
| `enrichment_type` | `string` | Nullable |
| `enrichment_payload_json` | `string` | Nullable |
| `business_name` | `string` | Nullable |
| `business_description` | `string` | Nullable |
| `business_meaning` | `string` | Nullable |
| `column_description` | `string` | Nullable |
| `classification` | `string` | Nullable |
| `sensitivity_label` | `string` | Nullable |
| `pii_flag` | `boolean` | Nullable |
| `pii_type` | `string` | Nullable |
| `data_domain` | `string` | Nullable |
| `data_owner` | `string` | Nullable |
| `data_steward` | `string` | Nullable |
| `usage_notes` | `string` | Nullable |
| `quality_notes` | `string` | Nullable |
| `review_status` | `string` | Nullable |
| `review_state` | `string` | Nullable |
| `activation_state` | `string` | Nullable |
| `is_active` | `boolean` | Nullable |
| `created_by_role` | `string` | Nullable |
| `source_notebook_type` | `string` | Nullable |
| `source_notebook_id` | `string` | Nullable |
| `activation_reason` | `string` | Nullable |
| `activated_by` | `string` | Nullable |
| `activated_at` | `timestamp` | Nullable |
| `requires_governance_review` | `boolean` | Nullable |
| `approval_policy` | `string` | Nullable |
| `governance_mode` | `string` | Nullable |
| `submitted_by` | `string` | Nullable |
| `submitted_at` | `timestamp` | Nullable |
| `reviewed_by` | `string` | Nullable |
| `reviewed_at` | `timestamp` | Nullable |
| `review_decision` | `string` | Nullable |
| `review_comment` | `string` | Nullable |
| `bypass_reason` | `string` | Nullable |
| `requires_post_review` | `boolean` | Nullable |
| `supersedes_enrichment_rule_id` | `string` | Nullable |
| `supersedes_record_id` | `string` | Nullable |
| `superseded_by_record_id` | `string` | Nullable |
| `effective_from` | `date` | Nullable |
| `effective_to` | `date` | Nullable |
| `created_at` | `timestamp` | Nullable |
| `created_by` | `string` | Nullable |
| `updated_at` | `timestamp` | Nullable |
| `updated_by` | `string` | Nullable |
| `run_id` | `string` | Nullable |
| `notebook_id` | `string` | Nullable |
| `notebook_registry_id` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_committed_at` | `timestamp` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
