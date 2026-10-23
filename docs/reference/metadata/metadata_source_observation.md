# METADATA_SOURCE_OBSERVATION

Store source evidence observed by one logical pipeline for one governed target, including source_table_name and target_table_name captured for that observation. run_id joins METADATA_PIPELINE_RUN.run_id for planned executions; _activity_id retains the actual Fabric activity shared by different attempts. Legacy and standalone observations may have no run_id. observation_status=observed means the run captured the evidence but has not accepted it; observation_status=committed records accepted incremental progress, and drift_committed records the Source Drift baseline. Warehouse publication_observed and publication_committed rows store target-only retry receipts with empty source identity and no watermark; they also cover Full Read and source-free writes.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)

## Used in Workflow Template

* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One observed or committed partition-state row within one logical notebook, source table, target table, and observation; target-only Warehouse publication receipt rows have an empty source identity.

**Primary key:** `observation_id` + `partition_value` + `observation_status`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → 1)**
via `run_id`

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `source_table_id` + `target_table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 25 |
| Business columns | 17 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `observation_id` | `string` | Identifier stored for `observation_id`. |
| `run_id` | `string` | Logical pipeline attempt ID shared with METADATA_PIPELINE_RUN.run_id. The real Fabric activity remains in _activity_id. Null or empty for legacy and standalone observations; recovered records retain the original run identity. |
| `source_table_id` | `string` | Identifier stored for `source_table_id`. |
| `source_table_name` | `string` | Source table name captured from the Catalogue when this observation was written; later renames do not change it. |
| `target_table_id` | `string` | Identifier stored for `target_table_id`. |
| `target_table_name` | `string` | Target table name captured from the Catalogue when this observation was written; later renames do not change it. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `partition_value` | `string` | String representation of the observed partition value. |
| `row_count` | `long` | Number of rows observed in the partition, or zero for a removal tombstone. |
| `min_change_value` | `string` | Earliest observed change-column value, or null for a removal tombstone. |
| `max_change_value` | `string` | Latest observed change-column value, or null for a removal tombstone. |
| `content_fingerprint` | `string` | Metadata Source Observation field `content_fingerprint`. |
| `is_present` | `boolean` | Whether the partition exists in this observation; false identifies a removal tombstone. |
| `observation_status` | `string` | Metadata Source Observation field `observation_status`. |
| `publication_payload_json` | `string` | Exact prepared-batch identity, originating pipeline run, real Fabric activity and publication timestamp staged before the physical write. Recovery verifies the Delta commit and target marker for Lakehouse writes, or the exact staged activity/timestamp pair for Warehouse writes. Target-only Warehouse receipt rows never advance source watermarks; legacy activity-only rows are not automatically promoted. |
| `execution_workspace_id` | `string` | Registered engineering workspace scope; distinct from the committing administrator workspace. Historical unassigned rows remain nullable until explicit migration. |
| `_legacy_environment_name` | `string` | Original deployment environment label retained during explicit stopped-workload metadata migration. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
