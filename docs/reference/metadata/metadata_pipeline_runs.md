# METADATA_PIPELINE_RUNS

**Purpose:** Pipeline run summary evidence for execution, guardrail, lineage, and catalogue status.

## Starter Kit usage

- **Written by notebook/template:** 02_pipeline.ipynb
- **Written by function or widget:** [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
- **Read by function or widget:** [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- **Related template step:** 02_pipeline.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `run_id` | `string` | Nullable |
| `agreement_id` | `string` | Nullable |
| `agreement_contract_version` | `string` | Nullable |
| `notebook_registry_id` | `string` | Nullable |
| `notebook_id` | `string` | Nullable |
| `notebook_type` | `string` | Nullable |
| `pipeline_name` | `string` | Nullable |
| `environment_name` | `string` | Nullable |
| `started_at` | `string` | Nullable |
| `completed_at` | `string` | Nullable |
| `status` | `string` | Nullable |
| `source_count` | `bigint` | Nullable |
| `target_count` | `bigint` | Nullable |
| `source_guardrail_status` | `string` | Nullable |
| `target_guardrail_status` | `string` | Nullable |
| `dq_status` | `string` | Nullable |
| `lineage_status` | `string` | Nullable |
| `catalogue_status` | `string` | Nullable |
| `message` | `string` | Nullable |
| `run_summary_json` | `string` | Nullable |
| `created_at` | `string` | Nullable |

## Related function reference

- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
