# METADATA_TARGET_PUBLICATION

Record whether one environment, activity, and governed target publication has physically succeeded or completed metadata finalization so retries do not repeat target mutations.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One deterministic target publication boundary for one activity and environment.

**Primary key:** `publication_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `target_table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 14 |
| Business columns | 6 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `publication_id` | `string` | Identifier stored for `publication_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `target_table_id` | `string` | Identifier stored for `target_table_id`. |
| `source_table_ids_json` | `string` | JSON payload stored for `source_table_ids_json`. |
| `load_strategy` | `string` | Metadata Target Publication field `load_strategy`. |
| `publication_status` | `string` | Metadata Target Publication field `publication_status`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
