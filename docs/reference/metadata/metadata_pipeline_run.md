# METADATA_PIPELINE_RUN

Records Test and Live operation participation, exact table contracts and execution outcomes.

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

`METADATA_DATA_CONTRACT` **(N → M)**
via `operations`

**Implementation details:** Whole-row CAS atomically publishes the parent and all operations/stages. Native operations retain table_id, source/target role, exact contract version/hash, destination, read/write mode, SQL hash and source associations. Live pins approval_id and compares these fields before operations. Profiling completion joins physical result snapshots. warnings_json contains variable sanitized diagnostics only. No project settings, full argument snapshots or configuration fingerprints are stored.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 22 |
| Business columns | 14 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `run_id` | `string` | Unique execution attempt and physical merge key; one authoritative row contains every Read/Write. |
| `approval_id` | `string` | Exact Governance decision retained in the Registry authority; Live runs pin this decision. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `execution_mode` | `string` | Metadata Pipeline Run field `execution_mode`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `started_at` | `timestamp` | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Whole-run outcome: incomplete, failed, succeeded or ungoverned_completed; operation success alone never completes a run. |
| `activation_revision` | `string` | Metadata Pipeline Run field `activation_revision`. |
| `boundary_completed` | `boolean` | Whether the explicit whole-run completion boundary finished; independent of operation success. |
| `operations` | `array<struct<operation_key:string,table_id:string,pipeline_role:string,contract_id:string,contract_version:int,payload_sha256:string,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>,read_mode:string,write_mode:string,query_sha256:string,source_table_ids:array<string>,incremental_target_table_id:string,status:string,started_at:timestamp,completed_at:timestamp,stages:array<struct<stage:string,status:string,evaluation_status:string>>>>` | Native Read/Write operation facts: table ID, role, exact contract version/hash, destination, modes, source associations, status, timing and stages. Query directly with explode(operations); no configuration join is required. |
| `profiling` | `array<struct<context_key:string,activity:string,status:string,results_persisted:boolean,empty_result:boolean,profile_snapshot_id:string,completed_at:string,reason:string,table_id:string,row_count:bigint,trigger:string,environment:string,pipeline_run_id:string,executed_at:string,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | Typed per-table activity outcomes and physical result snapshot completion markers. |
| `warnings_json` | `string` | Variable sanitized diagnostics; no configuration snapshots or activation authority. |
| `failures` | `array<struct<code:string,exception_type:string>>` | Native safe failure codes and exception class names; never raw exception messages. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
