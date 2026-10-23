# METADATA_EXECUTION_STATE

Engineering-owned run reservations and persistent cutover lock, separate from governance approvals.

## Writer functions

* [`setup_metadata_tables`](../../api/reference/setup_metadata_tables.md)

## Used in Workflow Template

* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Environment bootstrap

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One central coordination snapshot containing workspace-scoped reservations.

**Primary key:** `authority_id`

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
| `authority_id` | `string` | Identifier stored for `authority_id`. |
| `token` | `string` | Metadata Execution State field `token`. |
| `snapshot_json` | `string` | JSON payload stored for `snapshot_json`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
