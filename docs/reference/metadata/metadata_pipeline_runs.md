# METADATA_PIPELINE_RUNS

**Purpose:** Pipeline run summaries for execution, guardrail, lineage, and catalogue status.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `agreement_id` | `string` | No | Pipeline run summary writer | Metadata Pipeline Runs field `agreement_id`. |
| `agreement_version` | `string` | No | Pipeline run summary writer | Canonical agreement version associated with the row. |
| `environment_name` | `string` | No | Pipeline run summary writer | Metadata Pipeline Runs field `environment_name`. |
| `notebook_type` | `string` | No | Pipeline run summary writer | Metadata Pipeline Runs field `notebook_type`. |
| `started_at` | `timestamp` | Yes | Pipeline run summary writer | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Yes | Pipeline run summary writer | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Yes | Pipeline run summary writer | Pipeline run status recorded with the run summary. |
| `source_count` | `long` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `source_count`. |
| `target_count` | `long` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `target_count`. |
| `source_guardrail_status` | `string` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `source_guardrail_status`. |
| `target_guardrail_status` | `string` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `target_guardrail_status`. |
| `dq_status` | `string` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `dq_status`. |
| `lineage_status` | `string` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `lineage_status`. |
| `catalogue_status` | `string` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `catalogue_status`. |
| `message` | `string` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `message`. |
| `run_summary_json` | `string` | Yes | Pipeline run summary writer | Metadata Pipeline Runs field `run_summary_json`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Execution identity

`_activity_id` is the canonical execution identity. `started_at` comes from pipeline bootstrap, `completed_at` is captured when the run summary is written, and duration is derived from their difference.

## Related function reference

- [`widget_pipeline_bootstrap`](../../api/reference/widget_pipeline_bootstrap.md)
- [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
