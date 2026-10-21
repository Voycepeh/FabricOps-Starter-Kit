# METADATA_ACTIVATION_STATE

Single atomic central authority for environment activation revisions, immutable approval history, table contracts, writer ownership and running execution reservations.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One central authority row containing environment snapshots.

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
| `token` | `string` | Metadata Activation State field `token`. |
| `snapshot_json` | `string` | JSON payload stored for `snapshot_json`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
