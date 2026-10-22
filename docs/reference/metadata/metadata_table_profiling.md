# METADATA_TABLE_PROFILING

Mutable table-level profiling policies and per-environment/physical-context activity history, renewable claims and last successful completions; independent of frozen contracts and activation authority.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)
* [`setup_metadata_tables`](../../api/reference/setup_metadata_tables.md)
* [`widget_data_contract`](../../api/reference/widget_data_contract.md)

## Used in Workflow Template

* [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Environment bootstrap
* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Data Contract authoring
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One preinitialized central coordination row. snapshot_json contains Table ID policies and activity state keyed by Table ID, environment and physical bindings.

**Primary key:** `state_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 11 |
| Business columns | 3 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `state_id` | `string` | Identifier stored for `state_id`. |
| `token` | `string` | Metadata Table Profiling field `token`. |
| `snapshot_json` | `string` | JSON payload stored for `snapshot_json`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
