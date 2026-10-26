# METADATA_DATA_STEWARD

Identifies the people responsible for governing data.

## Writer functions

* [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md)

## Used in Workflow Template

* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Agreement intake

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One registered Data Steward.

**Primary key:** `steward_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">14</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">6</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--governance"><td><code>steward_id</code></td><td><code>string</code></td><td>Stable identifier for the steward row.</td></tr>
<tr class="metadata-column--governance"><td><code>steward_name</code></td><td><code>string</code></td><td>Human-readable steward name.</td></tr>
<tr class="metadata-column--governance"><td><code>steward_role</code></td><td><code>string</code></td><td>Configured steward role captured for the row.</td></tr>
<tr class="metadata-column--governance"><td><code>contact</code></td><td><code>string</code></td><td>Contact detail captured for the steward record.</td></tr>
<tr class="metadata-column--governance"><td><code>is_active</code></td><td><code>boolean</code></td><td>Whether the row is currently active.</td></tr>
<tr class="metadata-column--governance"><td><code>custom_fields_json</code></td><td><code>string</code></td><td>JSON payload stored for <code>custom_fields_json</code>.</td></tr>
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
