# METADATA_PIPELINE_RUN

Records explicitly finalized Test and Live execution outcomes against exact immutable definitions.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One row per execution with native observed operation/stage status, timing, finalization, profiling and safe failures.

**Primary key:** `run_id`

**Relationships:**

`METADATA_PIPELINE_REGISTRY` **(N → 1)**
via Not defined in the current implementation.

`METADATA_PIPELINE_DEFINITION` **(N → 1)**
via `definition_id`

**Implementation details:** Whole-row CAS atomically publishes the parent and all operations/stages. Expected configuration and exact participant contracts resolve through definition_id; Live pins approval_id. Profiling completion joins physical result snapshots. warnings_json contains variable sanitized operational-parameter diagnostics only.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 23 |
| Business columns | 15 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `run_id` | `string` | Unique execution attempt and physical merge key; one authoritative row contains every Read/Write. |
| `approval_id` | `string` | Exact Governance decision retained in the Registry authority; Live runs pin this decision. |
| `definition_id` | `string` | Exact immutable content-addressed pipeline/environment definition; missing or altered references fail closed. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `execution_mode` | `string` | Metadata Pipeline Run field `execution_mode`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `started_at` | `timestamp` | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Whole-run outcome: incomplete, failed, succeeded or ungoverned_completed; operation success alone never completes a run. |
| `activation_revision` | `string` | Metadata Pipeline Run field `activation_revision`. |
| `boundary_completed` | `boolean` | Whether the explicit whole-run completion boundary finished; independent of operation success. |
| `operations` | `array<struct<operation_key:string,status:string,started_at:timestamp,completed_at:timestamp,stages:array<struct<stage:string,status:string,evaluation_status:string>>>>` | Native observed Read/Write operations: operation key, status, timing and typed stages. Resolve declared table, contract and configuration through the exact definition; query with explode(operations). |
| `profiling` | `array<struct<context_key:string,activity:string,status:string,results_persisted:boolean,empty_result:boolean,profile_snapshot_id:string,completed_at:string,reason:string,table_id:string,row_count:bigint,trigger:string,environment:string,pipeline_run_id:string,executed_at:string,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | Typed per-table activity outcomes and physical result snapshot completion markers. |
| `warnings_json` | `string` | Variable sanitized operational-parameter diagnostics, including tested and actual values; no activation authority. |
| `failures` | `array<struct<code:string,exception_type:string>>` | Native safe failure codes and exception class names; never raw exception messages. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
