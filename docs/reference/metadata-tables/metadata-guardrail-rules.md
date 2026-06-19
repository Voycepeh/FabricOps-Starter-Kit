# METADATA_GUARDRAIL_RULES

**Purpose:** Approved or pending schema, freshness, profile behavior, and DQ guardrail intent.

## Workflow usage

- **Written by notebook/template:** 02_pipeline.ipynb, 03_governance.ipynb
- **Written by function or widget:** [`widget_author_schema_freshness_profile_rules`](../../api/reference/widget_author_schema_freshness_profile_rules.md), [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md), [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- **Read by function or widget:** [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- **Related template step:** 02_pipeline.ipynb, 03_governance.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `rule_key` | `string` | Nullable |
| `rule_id` | `string` | Nullable |
| `metadata_column_key` | `string` | Nullable |
| `metadata_table_key` | `string` | Nullable |
| `environment_name` | `string` | Nullable |
| `dataset_name` | `string` | Nullable |
| `table_name` | `string` | Nullable |
| `column_name` | `string` | Nullable |
| `guardrail_type` | `string` | Nullable |
| `rule_type` | `string` | Nullable |
| `rule_parameters_json` | `string` | Nullable |
| `severity` | `string` | Nullable |
| `description` | `string` | Nullable |
| `activation_state` | `string` | Nullable |
| `is_active` | `boolean` | Nullable |
| `review_status` | `string` | Nullable |
| `review_state` | `string` | Nullable |
| `created_by_role` | `string` | Nullable |
| `author_role` | `string` | Nullable |
| `created_by` | `string` | Nullable |
| `created_at` | `string` | Nullable |
| `approved_by` | `string` | Nullable |
| `approved_at` | `string` | Nullable |
| `suggestion_json` | `string` | Nullable |
| `action_type` | `string` | Nullable |
| `source_notebook_type` | `string` | Nullable |
| `source_notebook_id` | `string` | Nullable |
| `source_workspace_id` | `string` | Nullable |
| `activation_reason` | `string` | Nullable |
| `activated_by` | `string` | Nullable |
| `activated_at` | `string` | Nullable |
| `superseded_by_rule_key` | `string` | Nullable |
| `notes` | `string` | Nullable |
| `approval_required` | `boolean` | Nullable |
| `approval_bypassed` | `boolean` | Nullable |
| `requires_governance_review` | `boolean` | Nullable |
| `requires_post_review` | `boolean` | Nullable |
| `bypass_reason` | `string` | Nullable |
| `bypassed_by` | `string` | Nullable |
| `bypassed_at` | `string` | Nullable |
| `governance_mode` | `string` | Nullable |
| `approval_policy` | `string` | Nullable |
| `submitted_by` | `string` | Nullable |
| `submitted_at` | `string` | Nullable |
| `reviewed_by` | `string` | Nullable |
| `reviewed_at` | `string` | Nullable |
| `review_decision` | `string` | Nullable |
| `review_comment` | `string` | Nullable |
| `supersedes_rule_id` | `string` | Nullable |
| `supersedes_record_id` | `string` | Nullable |
| `superseded_by_record_id` | `string` | Nullable |
| `effective_from` | `string` | Nullable |
| `effective_to` | `string` | Nullable |
| `_committed_at` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md)
- [`widget_author_schema_freshness_profile_rules`](../../api/reference/widget_author_schema_freshness_profile_rules.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
