# METADATA_DATA_PROFILED

Stores statistics about table columns from profiling runs, making it easier to understand the data and track changes over time.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)
* [`profile_table`](../../api/reference/profile_table.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One column's statistics from one profiling snapshot.

**Primary key:** `profile_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id` + `column_id`

`METADATA_DATA_PROFILED_FREQUENCY` **(1 → N)**
via `profile_id`

**Implementation details:** See column-level profile metrics for a dataset snapshot. table_name and column_name record the names observed when written and do not follow later Catalogue renames.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">29</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">21</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>profile_id</code></td><td><code>string</code></td><td>Identifier stored for <code>profile_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>profile_snapshot_id</code></td><td><code>string</code></td><td>Identifier stored for <code>profile_snapshot_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across environment, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a column across environment, dataset, table, and column context.</td></tr>
<tr class="metadata-column--engineering"><td><code>environment_name</code></td><td><code>string</code></td><td>Environment name recorded for the metadata row.</td></tr>
<tr class="metadata-column--engineering"><td><code>data_type</code></td><td><code>string</code></td><td>Stable data type label recorded for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>column_name</code></td><td><code>string</code></td><td>Column name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>row_count</code></td><td><code>long</code></td><td>Observed total row count in the profiled dataset snapshot.</td></tr>
<tr class="metadata-column--engineering"><td><code>non_null_count</code></td><td><code>long</code></td><td>Observed non-null value count for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>null_count</code></td><td><code>long</code></td><td>Observed null value count for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>null_percent</code></td><td><code>double</code></td><td>Observed null percentage for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>distinct_count</code></td><td><code>long</code></td><td>Observed distinct value count for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>distinct_percent</code></td><td><code>double</code></td><td>Observed distinct percentage for the column.</td></tr>
<tr class="metadata-column--engineering"><td><code>mean_value</code></td><td><code>double</code></td><td>Observed mean value for numeric columns when available.</td></tr>
<tr class="metadata-column--engineering"><td><code>stddev_value</code></td><td><code>double</code></td><td>Observed standard deviation for numeric columns when available.</td></tr>
<tr class="metadata-column--engineering"><td><code>min_value</code></td><td><code>string</code></td><td>Observed minimum value captured as text.</td></tr>
<tr class="metadata-column--engineering"><td><code>percentile_25_value</code></td><td><code>double</code></td><td>Observed 25th percentile for numeric columns when available.</td></tr>
<tr class="metadata-column--engineering"><td><code>median_value</code></td><td><code>double</code></td><td>Observed median value for numeric columns when available.</td></tr>
<tr class="metadata-column--engineering"><td><code>percentile_75_value</code></td><td><code>double</code></td><td>Observed 75th percentile for numeric columns when available.</td></tr>
<tr class="metadata-column--engineering"><td><code>max_value</code></td><td><code>string</code></td><td>Observed maximum value captured as text.</td></tr>
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
