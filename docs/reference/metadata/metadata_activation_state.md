# METADATA_ACTIVATION_STATE

Records which pipeline releases are approved to run Live in each environment, together with the agreements and approvals behind them.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)
* [`setup_pipeline`](../../api/reference/setup_pipeline.md)
* [`widget_activate_pipeline`](../../api/reference/widget_activate_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One typed approval, participant, ownership, revision or reservation record, published with central authority.

**Primary key:** `record_id`

**Relationships:**

**Activated Pipeline (logical entity; 1 → N):** Each registered Pipeline UUID can have many immutable Activated Pipeline releases in the environment history. Activated Pipeline approvals and their exact participants are typed records in the canonical authority table.

**Live Pipeline Run (logical entity; 1 → N):** Each approved Activated Pipeline release authorizes many Live Pipeline Runs; registration alone never authorizes execution.

**Implementation details:** Single atomic central authority publishes authority, environment, approval, activation, participant, ownership, reservation and profiling_claim records with a central CAS token in one Delta MERGE. Native structs expose exact approval/participant/contract/binding identities, revisions, ownership and reservations; JSON retains authored configuration and frozen diagnostics only. Readers reject incomplete or corrupt publications. See the Activation State records maintainer guide for keys, nullability and Preview replacement instructions.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 21 |
| Business columns | 13 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `record_id` | `string` | Identifier stored for `record_id`. |
| `record_type` | `string` | Metadata Activation State field `record_type`. |
| `token` | `string` | Metadata Activation State field `token`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `parent_id` | `string` | Identifier stored for `parent_id`. |
| `authority` | `struct<record_count:bigint,content_sha256:string>` | Metadata Activation State field `authority`. |
| `environment` | `struct<revision:string>` | Metadata Activation State field `environment`. |
| `approval` | `struct<pipeline_id:string,activated_pipeline_id:string,pipeline_name:string,pipeline_version:string,testing_run_id:string,agreement_id:string,agreement_version:string,candidate_fingerprint:string,portable_fingerprint:string,project_configuration_json:string,operations:array<struct<operation:string,configuration_sha256:string,configuration_json:string>>,agreement_json:string,testing_evidence_json:string,warnings_json:string>` | Metadata Activation State field `approval`. |
| `activation` | `struct<pipeline_id:string,activated_pipeline_id:string>` | Metadata Activation State field `activation`. |
| `participant` | `struct<participant:string,table_id:string,is_source:boolean,is_target:boolean,contract_id:string,contract_version:int,payload_sha256:string,contract_environment:string,contract_status:string,contract_payload_json:string,candidate_contract_json:string,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>` | Metadata Activation State field `participant`. |
| `ownership` | `struct<table_id:string,contract_id:string,contract_version:int,payload_sha256:string,writer:string,readers:array<struct<pipeline_id:string>>,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>` | Metadata Activation State field `ownership`. |
| `reservation` | `struct<reservation_id:string,pipeline_id:string,mode:string,revision:string,activated_pipeline_id:string,tables:array<struct<table_id:string>>,destinations:array<struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | Metadata Activation State field `reservation`. |
| `profiling_claim` | `struct<claim_key:string,token:string,key:string,table_id:string,activity:string,trigger:string,execution_id:string,expires_at:timestamp,completed_at:timestamp,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>` | Metadata Activation State field `profiling_claim`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
