# METADATA_PROCESSING_STATE

Stores source observations, accepted checkpoints, Source Drift baselines and publication receipts so pipelines can resume and recover processing safely.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)
* [`pipeline_read`](../../api/reference/pipeline_read.md)

## Used in Workflow Template

* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One source snapshot partition/header, source-to-target progress member, or exact target publication receipt.

**Primary key:** `record_id`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → 1)**
via `run_id`

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `source_table_id` + `target_table_id`

`METADATA_PROCESSING_STATE` **(N → 1)**
via `publication_id`

**Implementation details:** record_type distinguishes source_observation, incremental_checkpoint, drift_baseline and publication_receipt. Only committed checkpoints and baselines are accepted progress. Each exact target publication has one typed receipt; source members reference it through publication_id and are acknowledged together in one Delta merge. Empty-source headers remain distinct from absent NULL/empty-string partitions. The metadata v2 maintainer guide documents the Preview cutover and recovery protocol.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 36 |
| Business columns | 28 |
| Audit columns | 8 |

## Implemented schema

<div class="metadata-schema-table" markdown="1">

| Column | Data type | Description |
| --- | --- | --- |
| `record_id` | `string` | Stable SHA-256 primary key for one typed record; acceptance updates the same staged record. |
| `record_type` | `string` | source_observation, incremental_checkpoint, drift_baseline, or publication_receipt. |
| `status` | `string` | observed for captured source observations; staged before target publication; committed only after exact physical publication verification. |
| `observation_id` | `string` | Identifier grouping the partitions of one captured source snapshot. |
| `run_id` | `string` | Originating logical pipeline attempt, shared with METADATA_PIPELINE_RUN.run_id; null for standalone execution. Recovery retains the original run. |
| `pipeline_id` | `string` | Stable pipeline identity when execution uses a pipeline plan. |
| `source_table_id` | `string` | Identifier stored for `source_table_id`. |
| `source_table_name` | `string` | Physical source table name captured with the observation; null on publication receipts. |
| `target_table_id` | `string` | Identifier stored for `target_table_id`. |
| `target_table_name` | `string` | Physical target table name captured at publication; null on unbound observations. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `observed_at` | `timestamp` | Original source capture timestamp; distinct from acknowledgement time. |
| `accepted_at` | `timestamp` | Timestamp of successful metadata acknowledgement, shared by the receipt and all members accepted in one merge; null before acceptance. |
| `partition_column` | `string` | Column defining observed source partitions, or the incremental watermark column. |
| `change_column` | `string` | Source column supplying minimum and maximum change values. |
| `watermark_type` | `string` | Source scalar type for lossless change-value bounds, including distinct timestamp and timestamp_ntz semantics. Numeric and temporal values can be cast explicitly for queries. |
| `partition_value` | `string` | Canonical source partition text; SQL null remains null and is distinct from an empty string. Null also applies to receipt and empty-source header rows. |
| `row_count` | `long` | Observed source-partition row count, or zero for an empty source/removal tombstone. |
| `min_change_value` | `string` | Lossless minimum change value encoded according to watermark_type; null for empty observations/removals. |
| `max_change_value` | `string` | Lossless maximum change value encoded according to watermark_type; used as progress only on committed incremental_checkpoint records. |
| `content_fingerprint` | `string` | Source partition content fingerprint for Source Drift comparison; independent of the publication batch fingerprint. |
| `is_present` | `boolean` | True for a present source partition; false for an absent partition or empty incremental aggregate; null when no source partition applies, including empty-source headers and receipts. |
| `publication_id` | `string` | Reference to the exact target-specific publication_receipt record_id; a receipt references itself. |
| `publication_batch_id` | `string` | Prepared business content, schema, source membership and processing fingerprint; stored only on the receipt. |
| `publication_activity_id` | `string` | Fabric activity whose atomic target write stamped the batch; recovery does not substitute the retry activity. |
| `publication_at` | `timestamp` | UTC timestamp stamped atomically with target rows; paired with publication_activity_id for verification. |
| `publication_input_rows` | `long` | Prepared batch row count. Warehouse append/overwrite recovery verifies the complete marker count. |
| `publication_strategy` | `string` | Physical append, overwrite, scd1 or scd2 strategy of the receipt. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |

</div>
