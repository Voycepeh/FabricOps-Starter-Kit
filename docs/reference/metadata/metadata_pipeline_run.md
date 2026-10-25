# METADATA_PIPELINE_RUN

Records explicitly finalized Test runs and Live execution outcomes, including their tables, operations, profiling results and warnings.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One row per execution attempt, with a native typed operations array for all declared Reads and Writes.

**Primary key:** `run_id`

**Relationships:**

`METADATA_PIPELINE_REGISTRY` **(N → 1)**
via `pipeline_id`

**Implementation details:** One authoritative run row atomically contains typed Read/Write operations and typed stages. Operation keys identify source/target roles and logical participants; nested fields expose exact table/contract identity, configuration hash, status and timing without JSON parsing. Readers verify complete operation membership against the candidate. Profiling markers remain in run_details_json and join persisted result snapshots.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 21 |
| Business columns | 13 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `run_id` | `string` | Unique execution attempt and physical merge key; one authoritative row contains every Read/Write. |
| `activated_pipeline_id` | `string` | Identifier stored for `activated_pipeline_id`. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `execution_mode` | `string` | Metadata Pipeline Run field `execution_mode`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `started_at` | `timestamp` | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Whole-run outcome: incomplete, failed, succeeded or ungoverned_completed; operation success alone never completes a run. |
| `candidate_fingerprint` | `string` | Metadata Pipeline Run field `candidate_fingerprint`. |
| `candidate_json` | `string` | Exact candidate identity, configuration and physical bindings retained for fingerprint verification. |
| `boundary_completed` | `boolean` | Whether the explicit whole-run completion boundary finished; independent of operation success. |
| `operations` | `array<struct<operation_key:string,table_id:string,status:string,started_at:timestamp,completed_at:timestamp,configuration_sha256:string,configuration_json:string,contract_id:string,contract_version:int,contract_payload_sha256:string,stages:array<struct<stage:string,status:string,evaluation_status:string>>>>` | Native array of typed Read/Write structs: operation_key, table_id, status, timing, exact frozen contract, configuration identity/JSON and typed stages. Query with explode(operations); no operational JSON parsing is required. |
| `run_details_json` | `string` | Frozen contract references, profiling events, warnings, sanitized failures and activation provenance; operations and completion authority are typed fields. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
