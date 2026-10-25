# METADATA_PIPELINE_RUN

Records explicitly finalized Test runs and Live execution outcomes, including their tables, operations, profiling results and warnings.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One run record per execution attempt plus one operation record per declared source/target role and logical participant.

**Primary key:** `record_id`

**Relationships:**

`METADATA_PIPELINE_REGISTRY` **(N → 1)**
via `pipeline_id`

**Implementation details:** Typed run/operation records share run_id and snapshot_token and publish in one Delta transaction. Only the completed run row is authoritative. Operation rows expose table, exact frozen contract, configuration identity, status and timing. Readers verify operation_count and operations_digest before reconstructing notebook results. Profiling markers remain in run_details_json on the run row and join persisted result snapshots.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 39 |
| Business columns | 31 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `record_id` | `string` | SHA-256 over run_id and record type, plus logical operation key for operation rows; physical merge key. |
| `record_type` | `string` | run for the sole authoritative whole-run outcome; operation for one declared Read/Write. |
| `snapshot_token` | `string` | Publication token shared by the parent and every operation in one atomic Delta transaction. |
| `run_id` | `string` | Execution attempt identity shared by the run and its operation rows; not a unique physical key. |
| `activated_pipeline_id` | `string` | Identifier stored for `activated_pipeline_id`. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `execution_mode` | `string` | Metadata Pipeline Run field `execution_mode`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `started_at` | `timestamp` | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Run: incomplete, failed, succeeded or ungoverned_completed. Operation: not_started, incomplete, failed or succeeded. |
| `candidate_fingerprint` | `string` | Metadata Pipeline Run field `candidate_fingerprint`. |
| `candidate_json` | `string` | Exact candidate identity and physical bindings on the run row; null on operation rows. |
| `run_details_json` | `string` | Run-level frozen contract references, profiling events, warnings, sanitized failures and activation provenance; excludes operations and completion authority. |
| `boundary_completed` | `boolean` | Whole-run completion boundary on the run row; operation success never sets this authority. |
| `operation_count` | `long` | Exact number of declared operation records expected in the verified snapshot. |
| `operations_digest` | `string` | SHA-256 over sorted typed operation identities and payloads; rejects partial or mismatched snapshots. |
| `operation_id` | `string` | Deterministic SHA-256 of run_id and the role-qualified logical operation key. |
| `operation_key` | `string` | Stable role:logical-participant identity within the run. |
| `role` | `string` | source or target for an operation row. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `operation_type` | `string` | Read for a source; Write for a target. |
| `contract_id` | `string` | Stable identifier for the contract row. |
| `contract_version` | `integer` | Version recorded for the contract row. |
| `contract_payload_sha256` | `string` | Exact frozen contract payload hash selected for this operation; null for No Contract. |
| `operation_started_at` | `timestamp` | Actual operation start timestamp; null for an unstarted operation or unknown historical timing. |
| `operation_completed_at` | `timestamp` | Actual operation completion timestamp; null for an unfinished operation or unknown historical timing. |
| `configuration_sha256` | `string` | Identity of the frozen processing configuration for this operation. |
| `configuration_json` | `string` | Exact extensible processing configuration for one operation, retained for candidate verification. |
| `stages_json` | `string` | Sanitized stage names, statuses and evaluation statuses for one operation. |
| `failure_code` | `string` | blocked for a blocking stage, failed for other operation failure; null otherwise. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
