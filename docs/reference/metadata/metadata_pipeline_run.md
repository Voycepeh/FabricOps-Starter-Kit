# METADATA_PIPELINE_RUN

One complete logical run, exact table mappings, operation results, warnings and pinned activation revision.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One pipeline execution attempt.

**Primary key:** `run_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 21 |
| Business columns | 13 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `run_id` | `string` | Identifier stored for `run_id`. |
| `activated_pipeline_id` | `string` | Identifier stored for `activated_pipeline_id`. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `execution_mode` | `string` | Metadata Pipeline Run field `execution_mode`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `started_at` | `timestamp` | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Pipeline run status recorded with the run summary. |
| `candidate_fingerprint` | `string` | Metadata Pipeline Run field `candidate_fingerprint`. |
| `candidate_json` | `string` | JSON payload stored for `candidate_json`. |
| `operation_summary_json` | `string` | JSON payload stored for `operation_summary_json`. |
| `execution_workspace_id` | `string` | Registered engineering workspace scope; distinct from the committing administrator workspace. Historical unassigned rows remain nullable until explicit migration. |
| `_legacy_environment_name` | `string` | Original deployment environment label retained during explicit stopped-workload metadata migration. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
