# METADATA_PIPELINE_RUN

Persist one complete logical pipeline execution, candidate identity and operation outcomes. Bootstrap never qualifies as successful Testing evidence. Live continues to use existing contract authority.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One logical pipeline run across all participating sources and targets.

**Primary key:** `run_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 20 |
| Business columns | 12 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `run_id` | `string` | Identifier stored for `run_id`. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `execution_mode` | `string` | Metadata Pipeline Run field `execution_mode`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `started_at` | `timestamp` | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Pipeline run status recorded with the run summary. |
| `qualifies_for_activation` | `boolean` | Metadata Pipeline Run field `qualifies_for_activation`. |
| `candidate_fingerprint` | `string` | Metadata Pipeline Run field `candidate_fingerprint`. |
| `candidate_json` | `string` | JSON payload stored for `candidate_json`. |
| `operation_summary_json` | `string` | JSON payload stored for `operation_summary_json`. |
| `failure_json` | `string` | JSON payload stored for `failure_json`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
