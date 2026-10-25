# METADATA_PIPELINE_DEFINITION

Stores complete immutable pipeline configuration once, shared by Test, approval and Live runs.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)
* [`setup_pipeline`](../../api/reference/setup_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One immutable pipeline/environment definition with native participants, contract references, destinations and settings.

**Primary key:** `definition_id`

**Relationships:**

`METADATA_DATA_CONTRACT` **(N → M)**
via `participants`

`METADATA_DATA_CATALOGUE` **(N → M)**
via `participants`

**Implementation details:** One complete append seals the definition; stable Delta transaction identity prevents concurrent duplicate insertion. Exact retained contract payloads reconstruct candidate identity and are hash-verified. Only project and operation settings remain variable configuration JSON. Orphaned definitions grant no authority.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 16 |
| Business columns | 8 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `definition_id` | `string` | Exact immutable content-addressed pipeline/environment definition; missing or altered references fail closed. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `candidate_fingerprint` | `string` | Metadata Pipeline Definition field `candidate_fingerprint`. |
| `project_configuration_json` | `string` | Variable sanitized project settings and authored transformation dependencies; no authority or lifecycle state. |
| `participants` | `array<struct<participant:string,table_id:string,roles:array<string>,contract_id:string,contract_version:int,payload_sha256:string>>` | Complete declared logical participants, global table IDs, roles and exact frozen contract references. |
| `operation_configurations` | `array<struct<operation_key:string,configuration_sha256:string,configuration_json:string>>` | Expected operation keys and variable settings sealed in the immutable definition. |
| `physical_bindings` | `array<struct<table_id:string,workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>` | Typed exact destinations: workspace, item, kind, schema and table, keyed by global table ID. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
