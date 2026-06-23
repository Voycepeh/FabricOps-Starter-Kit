# METADATA_NOTEBOOK_REGISTRY

**Purpose:** Active notebook registration records linking notebooks to agreement, environment, dataset, and pipeline context.

## Starter Kit usage

- **Written by notebook/template:** 02_pipeline.ipynb
- **Written by function or widget:** `widget_select_agreement`
- **Read by function or widget:** `get_selected_agreement`, [`write_pipeline_lineage`](../../api/reference/write_pipeline_lineage.md), [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
- **Related template step:** 02_pipeline.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `agreement_id` | `string` | Nullable |
| `environment_name` | `string` | Nullable |
| `dataset_name` | `string` | Nullable |
| `table_name` | `string` | Nullable |
| `topic` | `string` | Nullable |
| `pipeline_name` | `string` | Nullable |
| `notebook_type` | `string` | Nullable |
| `workspace_id` | `string` | Nullable |
| `workspace_name` | `string` | Nullable |
| `notebook_id` | `string` | Nullable |
| `notebook_name` | `string` | Nullable |
| `notebook_url` | `string` | Nullable |
| `user_name` | `string` | Nullable |
| `user_id` | `string` | Nullable |
| `registered_at` | `string` | Nullable |
| `registration_id` | `string` | Nullable |
| `agreement_contract_version` | `string` | Nullable |
| `registration_role` | `string` | Nullable |
| `registration_status` | `string` | Nullable |
| `superseded_at` | `string` | Nullable |
| `superseded_by_registration_id` | `string` | Nullable |

## Related function reference

- `get_selected_agreement`
- `widget_select_agreement`
- [`write_pipeline_lineage`](../../api/reference/write_pipeline_lineage.md)
- [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
