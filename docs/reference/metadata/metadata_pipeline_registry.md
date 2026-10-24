# METADATA_PIPELINE_REGISTRY

Keeps a permanent ID for each pipeline and records which notebook represents it in each environment. Renaming or promoting a notebook does not change the pipeline's identity.

## Writer functions

* [`setup_metadata_tables`](../../api/reference/setup_metadata_tables.md)
* [`setup_pipeline`](../../api/reference/setup_pipeline.md)

## Used in Workflow Template

* [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Environment bootstrap
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Configure the pipeline and whole-run boundary

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One pipeline registration per environment, plus one technical control row used to coordinate registration.

**Primary key:** `pipeline_id` + `environment_name`

**Relationships:**

`METADATA_PIPELINE_RUN` **(1 → N)**
via `pipeline_id` + `environment_name`

**Activated Pipeline (logical entity; 1 → N):** One registered Pipeline UUID has many immutable releases inside governance.METADATA_ACTIVATION_STATE; Activated Pipeline is a logical entity, not a separate Delta table.

**Implementation details:** Permanent UUIDv4 identity and environment-specific notebook bindings; registration never authorizes Live. A seeded Authority control row serializes binding transactions in this same table.

**Implementation details:** Permanent UUIDv4 identity and environment-specific notebook bindings; registration never authorizes Live. A seeded Authority control row serializes binding transactions in this same table.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 18 |
| Business columns | 10 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `pipeline_id` | `string` | Permanent system-generated UUIDv4 of the logical pipeline. The serialization control row uses central. |
| `environment_name` | `string` | Resolved environment; together with pipeline_id identifies one notebook binding. The control row uses *. |
| `workspace_id` | `string` | Workspace ID of the registered physical notebook; never part of the logical UUID. |
| `notebook_id` | `string` | Current physical Fabric notebook ID; promotion or explicit rebinding preserves the UUID. |
| `notebook_name` | `string` | Informational notebook display name; never used for identity matching or execution eligibility. |
| `registered_at` | `timestamp` | Timestamp when this environment binding was first registered; preserved by rebinding. |
| `registered_by` | `string` | Principal that first registered this environment binding; preserved by rebinding. |
| `updated_at` | `timestamp` | Timestamp of the most recent notebook binding or informational name update. |
| `registration_status` | `string` | Active or Retired for pipeline bindings; Authority identifies the single serialization control row. |
| `registry_token` | `string` | Compare-and-swap token updated with each binding mutation in the same Serializable Delta transaction. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
