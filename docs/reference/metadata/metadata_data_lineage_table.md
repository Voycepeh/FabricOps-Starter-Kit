# METADATA_DATA_LINEAGE_TABLE

**Purpose:** Source-to-target lineage evidence written by pipeline runs.

## Workflow usage

- **Written by notebook/template:** 02_pipeline.ipynb
- **Written by function or widget:** [`write_pipeline_lineage`](../../api/reference/write_pipeline_lineage.md)
- **Read by function or widget:** [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- **Related template step:** 02_pipeline.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `lineage_id` | `string` | Nullable |
| `dataset_name` | `string` | Nullable |
| `run_id` | `string` | Nullable |
| `source_table` | `string` | Nullable |
| `target_table` | `string` | Nullable |
| `source_table_key` | `string` | Nullable |
| `target_table_key` | `string` | Nullable |
| `transformation_steps_json` | `string` | Nullable |
| `created_at` | `string` | Nullable |
| `_committed_at` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- [`write_pipeline_lineage`](../../api/reference/write_pipeline_lineage.md)
