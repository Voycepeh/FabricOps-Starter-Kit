# METADATA_PIPELINE_REGISTRY

Coordinates Engineering registrations and Governance decisions through one atomic native authority.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)
* [`profile_table`](../../api/reference/profile_table.md)
* [`setup_pipeline`](../../api/reference/setup_pipeline.md)
* [`widget_activate_pipeline`](../../api/reference/widget_activate_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One central row: native registrations, approvals, selections, ownership and execution/profiling reservations.

**Primary key:** `authority_id`

**Relationships:**

`METADATA_PIPELINE_RUN` **(1 → N)**
via `approvals` + `reservations`

`METADATA_DATA_AGREEMENT` **(N → M)**
via `approvals`

`METADATA_DATA_CONTRACT` **(N → 1)**
via `table_ownership[].contract_id` + `table_ownership[].contract_version`

**Nested references (application-enforced):**

| Local field | Referenced field | Meaning |
| --- | --- | --- |
| `approvals[].testing_run_id` | `METADATA_PIPELINE_RUN.run_id` | Each nested approval retains one exact finalized Test Run; many approvals may reuse a Test. Application-enforced reference. |
| `approvals[].agreement_id` | `METADATA_DATA_AGREEMENT.agreement_id` | Composite reference with approvals[].agreement_version to one exact Agreement version, verified with its content hash. |
| `approvals[].agreement_version` | `METADATA_DATA_AGREEMENT.agreement_version` | Composite reference with approvals[].agreement_id; neither field is independently unique. |
| `table_ownership[].contract_id` | `METADATA_DATA_CONTRACT.contract_id` | Composite reference with table_ownership[].contract_version; ownership retains the exact approved table contract and payload hash. |
| `table_ownership[].contract_version` | `METADATA_DATA_CONTRACT.contract_version` | Composite reference with table_ownership[].contract_id; the referenced contract must match the owned table. |

**Implementation details:** A matched-only Delta compare-and-swap publishes all typed collections together. Registration, approval, admission, rebind and profiling share one token; no snapshot JSON or child-row insertion is authoritative. Exact finalized Test runs and Agreements resolve by retained content-checked references. There is no separate configuration table.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 17 |
| Business columns | 9 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `authority_id` | `string` | Singleton publication identity central; runtime writers never insert a missing authority. |
| `token` | `string` | Shared compare-and-swap fence for registration, approval, admission, rebind and profiling mutations. |
| `registrations` | `array<struct<pipeline_id:string,environment_name:string,workspace_id:string,notebook_id:string,notebook_name:string,registered_at:timestamp,registered_by:string,registration_status:string,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>` | Native permanent Pipeline UUID and environment notebook bindings; registration never permits Live. |
| `revisions` | `array<struct<environment_name:string,revision:string>>` | Native environment activation revisions published with selections and ownership. |
| `approvals` | `array<struct<approval_id:string,pipeline_id:string,environment_name:string,pipeline_name:string,pipeline_version:string,testing_run_id:string,testing_evidence_sha256:string,agreement_id:string,agreement_version:string,agreement_sha256:string,warnings:array<string>,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>` | Append-only decisions referencing complete finalized Test Runs and exact Agreement versions/hashes. |
| `selections` | `array<struct<environment_name:string,pipeline_id:string,approval_id:string>>` | Current approved decision per pipeline and environment, published atomically with ownership. |
| `table_ownership` | `array<struct<environment_name:string,table_id:string,contract_id:string,contract_version:int,payload_sha256:string,writer:string,readers:array<string>,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | Native exact contract, physical destination, writer and readers per environment/table. |
| `reservations` | `array<struct<environment_name:string,reservation_id:string,pipeline_id:string,mode:string,tables:array<string>,revision:string,destinations:array<struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>>` | Native Live reservations and transient rebind barriers protected by the shared authority token. |
| `profiling_claims` | `array<struct<claim_key:string,token:string,key:string,table_id:string,environment:string,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>,activity:string,trigger:string,expires_at:string,execution_id:string,completed_at:string>>` | Renewable native claims with exact owner tokens, physical context and expiry. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
