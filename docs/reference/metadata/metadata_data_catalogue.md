# METADATA_DATA_CATALOGUE

Lists registered tables and columns, where they are stored, their data types and whether they are still active.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)
* [`profile_table`](../../api/reference/profile_table.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One registered table or column in one environment.

**Primary key:** `environment_name` + `table_id` + `column_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

**Implementation details:** The current structural registry of known table and column assets. table_id identifies the logical table, and column_id identifies the logical column while its normalized column name remains the same. data_type stores the current structural datatype, and is_active indicates whether the asset currently exists. Datatype changes preserve column_id, removed columns become inactive, and returning columns reuse their deterministic ID. METADATA_DATA_PROFILED retains historical observations.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 28 |
| Business columns | 20 |
| Audit columns | 8 |

## Implemented schema

<div class="metadata-schema-table" markdown="1">

| Column | Data type | Description |
| --- | --- | --- |
| `metadata_level` | `string` | Metadata Data Catalogue field `metadata_level`. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `column_id` | `string` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `store_type` | `string` | Configured Fabric store type recorded for the profiled dataset. |
| `layer` | `string` | The configured medallion layer where the table is stored. |
| `schema_name` | `string` | Lakehouse or warehouse schema name recorded for the dataset when available. |
| `table_name` | `string` | Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it. |
| `column_name` | `string` | Column name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it. |
| `data_type` | `string` | Stable data type label recorded for the column. |
| `load_strategy` | `string` | Metadata Data Catalogue field `load_strategy`. |
| `load_strategy_parameters_json` | <div class="metadata-structured-type"><span class="metadata-structured-type__label">Struct</span><table class="metadata-nested-type" aria-label="Fields in load_strategy_parameters_json"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>watermark_column</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>key_columns</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>effective_column</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>tracked_columns</code></td><td><code>array&lt;string&gt;</code></td></tr></tbody></table></div> | Native Spark struct containing optional watermark, key, effective and tracked columns. The retained `_json` suffix is historical; this value is not JSON text. |
| `writer_workspace_id` | `string` | Identifier stored for `writer_workspace_id`. |
| `writer_notebook_id` | `string` | Identifier stored for `writer_notebook_id`. |
| `writer_notebook_name` | `string` | Human-readable name stored for `writer_notebook_name`. |
| `scheduled_refresh_json` | <div class="metadata-structured-type"><span class="metadata-structured-type__label">Struct</span><table class="metadata-nested-type" aria-label="Fields in scheduled_refresh_json"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>schedules</code></td><td><code>Array of structs</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.enabled</code></td><td><code>boolean</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.frequency</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.times</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.timezone</code></td><td><code>string</code></td></tr></tbody></table></div> | Native Spark struct containing captured status and ordered schedules (enabled, frequency, times and timezone). The retained `_json` suffix is historical; this value is not JSON text. |
| `profile_key_candidates_json` | <div class="metadata-structured-type"><span class="metadata-structured-type__label">Struct</span><table class="metadata-nested-type" aria-label="Fields in profile_key_candidates_json"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>max_combination_width</code></td><td><code>int</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>candidates</code></td><td><code>Array of structs</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.columns</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.column_count</code></td><td><code>int</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.row_count</code></td><td><code>bigint</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.distinct_count</code></td><td><code>bigint</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.uniqueness_percent</code></td><td><code>double</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.null_count</code></td><td><code>bigint</code></td></tr></tbody></table></div> | Native Spark struct containing discovery status, maximum combination width and ordered candidate metrics. Historical list-only candidates have null status and null maximum width. The retained `_json` suffix is historical; this value is not JSON text. |
| `first_profiled_at` | `timestamp` | Timestamp stored for `first_profiled_at`. |
| `last_profiled_at` | `timestamp` | Timestamp stored for `last_profiled_at`. |
| `is_active` | `boolean` | Whether the row is currently active. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |

</div>
