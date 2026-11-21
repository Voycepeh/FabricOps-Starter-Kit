# METADATA_DATA_LINEAGE

Stores scalar Run/output/source column dependencies for Power BI and impact queries.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One finalized Run/Write/output/source/dependency type, with explicit constant, row-set and gap facts.

**Primary key:** `lineage_id`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → 1)**
via `run_id`

`METADATA_DATA_CATALOGUE` **(N → M)**
via `source_asset_workspace_id` + `source_table_id` + `source_asset_type` + `target_asset_workspace_id` + `target_table_id` + `target_asset_type`

**Implementation details:** Finalization derives immutable lineage_version=1 facts from the exact committed Run graph. Source/target physical Catalogue identities and column IDs, dependency_type, coverage, publication status and transformation summaries are scalar columns; no JSON expansion is required for reporting. Detailed graphs remain in Run operations for drill-through and rebuilding. Append transaction identities and exact read-back make retries idempotent without business-write replay. Setup additively evolves historical activity layouts, retaining old rows and extension columns unchanged. Historical rows have null lineage_version and must be excluded from dependency reports. Rows describe Write input, not retained target history. Run and projection are separate Delta commits; projection failure is explicit and independently retryable.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">40</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">32</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>lineage_id</code></td><td><code>string</code></td><td>Identifier stored for <code>lineage_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>lineage_version</code></td><td><code>integer</code></td><td>Metadata Data Lineage field <code>lineage_version</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>record_type</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>record_type</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>run_id</code></td><td><code>string</code></td><td>Identifier stored for <code>run_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_id</code></td><td><code>string</code></td><td>Identifier stored for <code>pipeline_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>execution_workspace_id</code></td><td><code>string</code></td><td>Identifier stored for <code>execution_workspace_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>operation_key</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>operation_key</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>run_status</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>run_status</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>operation_status</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>operation_status</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>publication_status</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>publication_status</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>write_mode</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>write_mode</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>detector</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>detector</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>scope</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>scope</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>coverage</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>coverage</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>target_asset_workspace_id</code></td><td><code>string</code></td><td>Identifier stored for <code>target_asset_workspace_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>target_table_id</code></td><td><code>string</code></td><td>Identifier stored for <code>target_table_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>target_asset_type</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>target_asset_type</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>target_column_id</code></td><td><code>string</code></td><td>Identifier stored for <code>target_column_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>target_column_name</code></td><td><code>string</code></td><td>Human-readable name stored for <code>target_column_name</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_asset_workspace_id</code></td><td><code>string</code></td><td>Identifier stored for <code>source_asset_workspace_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_table_id</code></td><td><code>string</code></td><td>Identifier stored for <code>source_table_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_asset_type</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>source_asset_type</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_column_id</code></td><td><code>string</code></td><td>Identifier stored for <code>source_column_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_column_name</code></td><td><code>string</code></td><td>Human-readable name stored for <code>source_column_name</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>dependency_type</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>dependency_type</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>gap_codes</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>gap_codes</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>transformation_operations</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>transformation_operations</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>transformation_count</code></td><td><code>integer</code></td><td>Metadata Data Lineage field <code>transformation_count</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>output_node_id</code></td><td><code>string</code></td><td>Identifier stored for <code>output_node_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_node_id</code></td><td><code>string</code></td><td>Identifier stored for <code>source_node_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>omitted_output_count</code></td><td><code>integer</code></td><td>Metadata Data Lineage field <code>omitted_output_count</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_run_sha256</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>source_run_sha256</code>.</td></tr>
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
