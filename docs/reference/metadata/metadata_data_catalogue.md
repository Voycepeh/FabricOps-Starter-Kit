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

**Grain:** One current table or column observation in one workspace.

**Primary key:** `workspace_id` + `table_id` + `column_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

**Implementation details:** The current structural registry of known table and column assets. Processing parameters, Scheduled Refresh and key-candidate discovery use validated physical JSON strings with logical dictionaries/lists in application code. table_id identifies the logical table, and column_id identifies the logical column while its normalized column name remains the same. data_type stores the current structural datatype, and is_active indicates whether the asset currently exists. Datatype changes preserve column_id, removed columns become inactive, and returning columns reuse their deterministic ID. METADATA_DATA_PROFILED retains historical observations.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">28</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">20</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>metadata_level</code></td><td><code>string</code></td><td>Metadata Data Catalogue field <code>metadata_level</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a column across workspace, dataset, table, and column context.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>store_type</code></td><td><code>string</code></td><td>Configured Fabric store type recorded for the profiled dataset.</td></tr>
<tr class="metadata-column--engineering"><td><code>layer</code></td><td><code>string</code></td><td>The configured medallion layer where the table is stored.</td></tr>
<tr class="metadata-column--engineering"><td><code>schema_name</code></td><td><code>string</code></td><td>Lakehouse or warehouse schema name recorded for the dataset when available.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_name</code></td><td><code>string</code></td><td>Column name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>data_type</code></td><td><code>string</code></td><td>Stable data type label recorded for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>load_strategy</code></td><td><code>string</code></td><td>Metadata Data Catalogue field <code>load_strategy</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>load_strategy_parameters_json</code></td><td><code>string</code></td><td>Native Spark struct containing optional watermark, key, effective and tracked columns. The retained <code>_json</code> suffix is historical; this value is not JSON text.</td></tr>
<tr class="metadata-column--engineering"><td><code>writer_workspace_id</code></td><td><code>string</code></td><td>Identifier stored for <code>writer_workspace_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>writer_notebook_id</code></td><td><code>string</code></td><td>Identifier stored for <code>writer_notebook_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>writer_notebook_name</code></td><td><code>string</code></td><td>Human-readable name stored for <code>writer_notebook_name</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>scheduled_refresh_json</code></td><td><code>string</code></td><td>Native Spark struct containing captured status and ordered schedules (enabled, frequency, times and timezone). The retained <code>_json</code> suffix is historical; this value is not JSON text.</td></tr>
<tr class="metadata-column--engineering"><td><code>profile_key_candidates_json</code></td><td><code>string</code></td><td>Native Spark struct containing discovery status, maximum combination width and ordered candidate metrics. Historical list-only candidates have null status and null maximum width. The retained <code>_json</code> suffix is historical; this value is not JSON text.</td></tr>
<tr class="metadata-column--engineering"><td><code>first_profiled_at</code></td><td><code>timestamp</code></td><td>Timestamp stored for <code>first_profiled_at</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>last_profiled_at</code></td><td><code>timestamp</code></td><td>Timestamp stored for <code>last_profiled_at</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>is_active</code></td><td><code>boolean</code></td><td>Whether the row is currently active.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_by</code></td><td><code>string</code></td><td>User principal or runtime identity that committed the metadata row.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_at</code></td><td><code>timestamp</code></td><td>Timestamp when the metadata row was committed.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_id</code></td><td><code>string</code></td><td>Fabric workspace identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_name</code></td><td><code>string</code></td><td>Fabric workspace name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_name</code></td><td><code>string</code></td><td>Fabric notebook name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_metadata_lakehouse_name</code></td><td><code>string</code></td><td>Configured metadata lakehouse name used for the write.</td></tr>
<tr class="metadata-column--audit"><td><code>_activity_id</code></td><td><code>string</code></td><td>Fabric execution activity identifier for the current notebook or pipeline run.</td></tr>
</tbody></table>
</div>
