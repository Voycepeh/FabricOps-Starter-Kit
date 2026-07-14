# METADATA_DATA_LINEAGE

**Purpose:** Metadata Data Lineage metadata table.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `lineage_event_id` | `string` | No | FabricOps workflow | Metadata Data Lineage field `lineage_event_id`. |
| `activity_id` | `string` | No | FabricOps workflow | Metadata Data Lineage field `activity_id`. |
| `notebook_id` | `string` | No | FabricOps workflow | Metadata Data Lineage field `notebook_id`. |
| `notebook_name` | `string` | No | FabricOps workflow | Metadata Data Lineage field `notebook_name`. |
| `workspace_id` | `string` | No | FabricOps workflow | Metadata Data Lineage field `workspace_id`. |
| `workspace_name` | `string` | No | FabricOps workflow | Metadata Data Lineage field `workspace_name`. |
| `metadata_table_key` | `string` | No | FabricOps workflow | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `schema_fingerprint` | `string` | No | FabricOps workflow | Metadata Data Lineage field `schema_fingerprint`. |
| `profile_role` | `string` | No | FabricOps workflow | Metadata Data Lineage field `profile_role`. |
| `profiled_at` | `timestamp` | No | FabricOps workflow | Metadata Data Lineage field `profiled_at`. |
| `committed_by` | `string` | No | FabricOps workflow | Metadata Data Lineage field `committed_by`. |
| `environment_name` | `string` | Yes | FabricOps workflow | Metadata Data Lineage field `environment_name`. |
| `metadata_lakehouse_name` | `string` | Yes | FabricOps workflow | Metadata Data Lineage field `metadata_lakehouse_name`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |
