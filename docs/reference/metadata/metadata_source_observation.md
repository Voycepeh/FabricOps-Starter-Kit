# METADATA_SOURCE_OBSERVATION

Store source evidence observed by one logical pipeline for one governed target. observation_status=observed means the run captured the evidence but has not accepted it; observation_status=committed means the associated physical target write succeeded and accepted it as the Source Stability baseline.

## Writer functions

* [`observe_table`](../../api/reference/observe_table.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Source guardrails

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One observed or committed partition-state row within one logical notebook, source table, target table, and observation.

**Primary key:** `observation_id` + `partition_value` + `observation_status`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `source_table_id` + `target_table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 19 |
| Business columns | 11 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `observation_id` | `string` | Identifier stored for `observation_id`. |
| `source_table_id` | `string` | Identifier stored for `source_table_id`. |
| `target_table_id` | `string` | Identifier stored for `target_table_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `partition_value` | `string` | String representation of the observed partition value. |
| `row_count` | `long` | Number of rows observed in the partition, or zero for a removal tombstone. |
| `min_change_value` | `string` | Earliest observed change-column value, or null for a removal tombstone. |
| `max_change_value` | `string` | Latest observed change-column value, or null for a removal tombstone. |
| `content_fingerprint` | `string` | Metadata Source Observation field `content_fingerprint`. |
| `is_present` | `boolean` | Whether the partition exists in this observation; false identifies a removal tombstone. |
| `observation_status` | `string` | Metadata Source Observation field `observation_status`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
