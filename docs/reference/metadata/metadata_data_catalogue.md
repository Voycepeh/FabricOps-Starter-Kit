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

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr><td><code>metadata_level</code></td><td><code>string</code></td><td>Metadata Data Catalogue field <code>metadata_level</code>.</td></tr>
<tr><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across environment, dataset, and table context.</td></tr>
<tr><td><code>column_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a column across environment, dataset, table, and column context.</td></tr>
<tr><td><code>environment_name</code></td><td><code>string</code></td><td>Environment name recorded for the metadata row.</td></tr>
<tr><td><code>store_type</code></td><td><code>string</code></td><td>Configured Fabric store type recorded for the profiled dataset.</td></tr>
<tr><td><code>layer</code></td><td><code>string</code></td><td>The configured medallion layer where the table is stored.</td></tr>
<tr><td><code>schema_name</code></td><td><code>string</code></td><td>Lakehouse or warehouse schema name recorded for the dataset when available.</td></tr>
<tr><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr><td><code>column_name</code></td><td><code>string</code></td><td>Column name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr><td><code>data_type</code></td><td><code>string</code></td><td>Stable data type label recorded for the column.</td></tr>
<tr><td><code>load_strategy</code></td><td><code>string</code></td><td>Metadata Data Catalogue field <code>load_strategy</code>.</td></tr>
<tr><td><code>load_strategy_parameters_json</code></td><td><details class="metadata-structured-type"><summary>Struct</summary><table class="metadata-nested-type" aria-label="Fields in load_strategy_parameters_json"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>watermark_column</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>key_columns</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>effective_column</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>tracked_columns</code></td><td><code>array&lt;string&gt;</code></td></tr></tbody></table></details></td><td>Native Spark struct containing optional watermark, key, effective and tracked columns. The retained <code>_json</code> suffix is historical; this value is not JSON text.</td></tr>
<tr><td><code>writer_workspace_id</code></td><td><code>string</code></td><td>Identifier stored for <code>writer_workspace_id</code>.</td></tr>
<tr><td><code>writer_notebook_id</code></td><td><code>string</code></td><td>Identifier stored for <code>writer_notebook_id</code>.</td></tr>
<tr><td><code>writer_notebook_name</code></td><td><code>string</code></td><td>Human-readable name stored for <code>writer_notebook_name</code>.</td></tr>
<tr><td><code>scheduled_refresh_json</code></td><td><details class="metadata-structured-type"><summary>Struct</summary><table class="metadata-nested-type" aria-label="Fields in scheduled_refresh_json"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>schedules</code></td><td><code>Array of structs</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.enabled</code></td><td><code>boolean</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.frequency</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.times</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>schedules.timezone</code></td><td><code>string</code></td></tr></tbody></table></details></td><td>Native Spark struct containing captured status and ordered schedules (enabled, frequency, times and timezone). The retained <code>_json</code> suffix is historical; this value is not JSON text.</td></tr>
<tr><td><code>profile_key_candidates_json</code></td><td><details class="metadata-structured-type"><summary>Struct</summary><table class="metadata-nested-type" aria-label="Fields in profile_key_candidates_json"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>max_combination_width</code></td><td><code>int</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>candidates</code></td><td><code>Array of structs</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.columns</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.column_count</code></td><td><code>int</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.row_count</code></td><td><code>bigint</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.distinct_count</code></td><td><code>bigint</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.uniqueness_percent</code></td><td><code>double</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>candidates.null_count</code></td><td><code>bigint</code></td></tr></tbody></table></details></td><td>Native Spark struct containing discovery status, maximum combination width and ordered candidate metrics. Historical list-only candidates have null status and null maximum width. The retained <code>_json</code> suffix is historical; this value is not JSON text.</td></tr>
<tr><td><code>first_profiled_at</code></td><td><code>timestamp</code></td><td>Timestamp stored for <code>first_profiled_at</code>.</td></tr>
<tr><td><code>last_profiled_at</code></td><td><code>timestamp</code></td><td>Timestamp stored for <code>last_profiled_at</code>.</td></tr>
<tr><td><code>is_active</code></td><td><code>boolean</code></td><td>Whether the row is currently active.</td></tr>
<tr><td><code>_committed_by</code></td><td><code>string</code></td><td>User principal or runtime identity that committed the metadata row.</td></tr>
<tr><td><code>_committed_at</code></td><td><code>timestamp</code></td><td>Timestamp when the metadata row was committed.</td></tr>
<tr><td><code>_workspace_id</code></td><td><code>string</code></td><td>Fabric workspace identifier captured from runtime audit context.</td></tr>
<tr><td><code>_workspace_name</code></td><td><code>string</code></td><td>Fabric workspace name captured from runtime audit context.</td></tr>
<tr><td><code>_notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured from runtime audit context.</td></tr>
<tr><td><code>_notebook_name</code></td><td><code>string</code></td><td>Fabric notebook name captured from runtime audit context.</td></tr>
<tr><td><code>_metadata_lakehouse_name</code></td><td><code>string</code></td><td>Configured metadata lakehouse name used for the write.</td></tr>
<tr><td><code>_activity_id</code></td><td><code>string</code></td><td>Fabric execution activity identifier for the current notebook or pipeline run.</td></tr>
</tbody></table>
</div>
