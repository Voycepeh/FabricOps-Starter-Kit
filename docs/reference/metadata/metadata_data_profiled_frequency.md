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

**Composite foreign key (checked by FabricOps):** (`workspace_id` + `table_id` + `asset_type`) → [METADATA_DATA_CATALOGUE](metadata_data_catalogue.md) (`workspace_id` + `table_id` + `asset_type`).
FabricOps checks the three columns together against one active Catalogue row before saving new observations.

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `workspace_id` + `table_id` + `asset_type`

`METADATA_DATA_PROFILED` **(N → 1)**
via `profile_id`

**Implementation details:** New frequency snapshots require one active physical Catalogue asset. Frequency distributions retain asset_type, the common table_id and column_id, workspace, column name and datatype. File rows also retain Run ID and role. Independently scheduled Frequency Profiling owns its activity snapshot and leaves profile_id null; combined standalone profiling may link a statistical Profile. Captured names do not follow later renames.

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
<tr class="metadata-column--engineering"><td><code>asset_type</code></td><td><code>string</code></td><td>Explicit asset discriminator: TABLE or FILE. Historical null values with table_id are TABLE.</td></tr>
<tr class="metadata-column--engineering"><td><code>run_id</code></td><td><code>string</code></td><td>Identifier stored for <code>run_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_role</code></td><td><code>string</code></td><td>Participation role: source for a Read or target for a Write.</td></tr>
<tr class="metadata-column--engineering"><td><code>frequency_id</code></td><td><code>string</code></td><td>Identifier stored for <code>frequency_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profile_id</code></td><td><code>string</code></td><td>Identifier stored for <code>profile_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profile_snapshot_id</code></td><td><code>string</code></td><td>Identifier stored for <code>profile_snapshot_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Common operational asset key for TABLE or FILE assets across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a column across workspace, dataset, asset, and column context.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_name</code></td><td><code>string</code></td><td>Column name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>data_type</code></td><td><code>string</code></td><td>Stable data type label recorded for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>ID of the Fabric workspace that contains the physical asset. For new rows, this is part of the Catalogue reference. Historical rows may carry the earlier workspace scope.</td></tr>
<tr class="metadata-column--engineering"><td><code>value</code></td><td><code>string</code></td><td>Metadata Data Profiled Frequency field <code>value</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>frequency_count</code></td><td><code>long</code></td><td>Metadata Data Profiled Frequency field <code>frequency_count</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>frequency_percent</code></td><td><code>double</code></td><td>Metadata Data Profiled Frequency field <code>frequency_percent</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>frequency_rank</code></td><td><code>integer</code></td><td>Metadata Data Profiled Frequency field <code>frequency_rank</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profiled_row_count</code></td><td><code>long</code></td><td>Metadata Data Profiled Frequency field <code>profiled_row_count</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profiled_non_null_count</code></td><td><code>long</code></td><td>Metadata Data Profiled Frequency field <code>profiled_non_null_count</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profile_scope</code></td><td><code>string</code></td><td>Profile input scope: full_table, bounded_selection (sampled selection-only statistics), or supplied_dataframe (physical coverage unverified). Historical rows may have null scope.</td></tr>
<tr class="metadata-column--engineering"><td><code>profiling_max_rows</code></td><td><code>long</code></td><td>Requested positive row bound for bounded profiling; null means no row bound. Does not guarantee a physical scan of only this many rows.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_by</code></td><td><code>string</code></td><td>User principal or runtime identity that committed the metadata row.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_at</code></td><td><code>timestamp</code></td><td>Timestamp when the metadata row was committed.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_id</code></td><td><code>string</code></td><td>ID of the executing notebook’s Fabric workspace, captured when the metadata row was written.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_name</code></td><td><code>string</code></td><td>Display name of the executing notebook’s Fabric workspace, captured when the metadata row was written.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_name</code></td><td><code>string</code></td><td>Fabric notebook name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_metadata_lakehouse_name</code></td><td><code>string</code></td><td>Configured metadata lakehouse name used for the write.</td></tr>
<tr class="metadata-column--audit"><td><code>_activity_id</code></td><td><code>string</code></td><td>Fabric execution activity identifier for the current notebook or pipeline run.</td></tr>
</tbody></table>
</div>

## Automatic column cleanup

`setup_metadata_tables()` removes only the explicitly retired columns below. It preserves canonical rows, all eight audit columns and other extension columns. If a populated value cannot be proved redundant, setup fails for this table with data preserved.

| Retired column | Removal condition |
| --- | --- |
| `metadata_column_key` | Every value is SQL NULL |
| `profiled_at` | SQL NULL or equal to `_committed_at` |
| `source_id` | SQL NULL or equal to `table_id` |

See [`setup_metadata_tables`](../../api/reference/setup_metadata_tables.md) for transaction results and the Delta recovery boundary.
