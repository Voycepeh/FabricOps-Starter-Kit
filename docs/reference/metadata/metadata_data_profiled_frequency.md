# METADATA_DATA_PROFILED_FREQUENCY

Shows which values appear most often in a column and how frequently they occur.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)
* [`profile_table`](../../api/reference/profile_table.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One recorded value and its frequency for a column in a profiling snapshot.

**Primary key:** `frequency_id`

**Relationships:**

`METADATA_DATA_PROFILED` **(N → 1)**
via `profile_id`

**Implementation details:** Frequency distributions retain Table ID, Column ID, workspace, captured names and datatype. Independently scheduled Frequency Profiling owns its activity snapshot and leaves profile_id null; combined standalone profiling may link a statistical Profile. Captured names do not follow later renames.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">23</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">15</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>frequency_id</code></td><td><code>string</code></td><td>Identifier stored for <code>frequency_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profile_id</code></td><td><code>string</code></td><td>Identifier stored for <code>profile_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profile_snapshot_id</code></td><td><code>string</code></td><td>Identifier stored for <code>profile_snapshot_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a column across workspace, dataset, table, and column context.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_name</code></td><td><code>string</code></td><td>Column name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>data_type</code></td><td><code>string</code></td><td>Stable data type label recorded for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>value</code></td><td><code>string</code></td><td>Metadata Data Profiled Frequency field <code>value</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>frequency_count</code></td><td><code>long</code></td><td>Metadata Data Profiled Frequency field <code>frequency_count</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>frequency_percent</code></td><td><code>double</code></td><td>Metadata Data Profiled Frequency field <code>frequency_percent</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>frequency_rank</code></td><td><code>integer</code></td><td>Metadata Data Profiled Frequency field <code>frequency_rank</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profiled_row_count</code></td><td><code>long</code></td><td>Metadata Data Profiled Frequency field <code>profiled_row_count</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profiled_non_null_count</code></td><td><code>long</code></td><td>Metadata Data Profiled Frequency field <code>profiled_non_null_count</code>.</td></tr>
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
