# METADATA_DATA_ACCESS

Records observed OneLake roles, workspace assignments, item access and supplied user membership for registered Lakehouse tables. It does not establish effective access.

## Writer functions

* [`scan_onelake_role_members`](../../api/reference/scan_onelake_role_members.md)

## Used in Workflow Template

* [`ad hoc Fabric notebook`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — OneLake membership inspection

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One observed permission for a principal or access selector on a table during one scan.

**Primary key:** `access_id`

**Composite foreign key (checked by FabricOps):** (`asset_workspace_id` + `table_id` + `asset_type`) → [METADATA_DATA_CATALOGUE](metadata_data_catalogue.md) (`asset_workspace_id` + `table_id` + `asset_type`).
FabricOps checks the three columns together against one active Catalogue row before saving new observations.

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `asset_workspace_id` + `table_id` + `asset_type`

**Implementation details:** The single scan_onelake_role_members scanner maps observed permissions to active Catalogue TABLE assets by physical workspace and item. Before saving, it verifies one active physical Catalogue parent. principal_object_id retains the API identity where known; supplied users retain their originating group in permission_details_json. That JSON also preserves role rules, restrictions and raw item permissions. New rows have access_verification_status UNVERIFIED. Existing SQL and other historical snapshots remain unchanged.

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
<tr class="metadata-column--engineering"><td><code>access_id</code></td><td><code>string</code></td><td>Stable identifier for one observed permission and assignment path in a scan snapshot.</td></tr>
<tr class="metadata-column--engineering"><td><code>user_principal</code></td><td><code>string</code></td><td>User UPN, originating principal object ID, or unresolved selector recorded for the observation.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Common operational asset key for TABLE or FILE assets across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>asset_workspace_id</code></td><td><code>string</code></td><td>ID of the Fabric workspace that contains the physical asset. For new rows, this is part of the Catalogue reference.</td></tr>
<tr class="metadata-column--engineering"><td><code>asset_type</code></td><td><code>string</code></td><td>Explicit asset discriminator: TABLE or FILE. Historical null values with table_id are TABLE.</td></tr>
<tr class="metadata-column--engineering"><td><code>access_level</code></td><td><code>string</code></td><td>Observed permission scope: ONELAKE_PATH, WORKSPACE_ROLE, or ITEM_ACCESS. Historical rows can retain SQL classes.</td></tr>
<tr class="metadata-column--engineering"><td><code>access_value</code></td><td><code>string</code></td><td>Observed OneLake action, workspace role name, or UNDECODED_ITEM_PERMISSION for raw portal permissions; historical rows can retain SQL permission names.</td></tr>
<tr class="metadata-column--engineering"><td><code>access_state</code></td><td><code>string</code></td><td>Observed rule effect or assignment state; this is not a confirmation of effective access.</td></tr>
<tr class="metadata-column--engineering"><td><code>access_snapshot_id</code></td><td><code>string</code></td><td>Identifier grouping permission rows captured in the same access inventory snapshot.</td></tr>
<tr class="metadata-column--engineering"><td><code>user_type</code></td><td><code>string</code></td><td>Observed principal type, USER for supplied user mappings, or FABRIC_ITEM_MEMBERS for unresolved automatic selectors.</td></tr>
<tr class="metadata-column--engineering"><td><code>role_name</code></td><td><code>string</code></td><td>Observed OneLake or workspace role; historical SQL snapshots can retain database role names.</td></tr>
<tr class="metadata-column--engineering"><td><code>permission_source</code></td><td><code>string</code></td><td>Observed permission surface: OneLake role, workspace role, or item access. Retained historical snapshots may use earlier source labels.</td></tr>
<tr class="metadata-column--engineering"><td><code>database_name</code></td><td><code>string</code></td><td>Lakehouse item ID for current OneLake observations; historical snapshots may retain SQL database names.</td></tr>
<tr class="metadata-column--engineering"><td><code>schema_name</code></td><td><code>string</code></td><td>Lakehouse or warehouse schema name recorded for the dataset when available.</td></tr>
<tr class="metadata-column--engineering"><td><code>object_name</code></td><td><code>string</code></td><td>Database object name covered by the observed permission when applicable.</td></tr>
<tr class="metadata-column--engineering"><td><code>object_type</code></td><td><code>string</code></td><td>Database object type covered by the observed permission when applicable.</td></tr>
<tr class="metadata-column--engineering"><td><code>principal_object_id</code></td><td><code>string</code></td><td>Entra object ID where established by the API. Null for caller-supplied users and automatic selectors; original group identity remains in permission_details_json.</td></tr>
<tr class="metadata-column--engineering"><td><code>access_verification_status</code></td><td><code>string</code></td><td>New OneLake inventory rows are UNVERIFIED: observed assignments and supplied memberships do not prove effective access.</td></tr>
<tr class="metadata-column--engineering"><td><code>permission_details_json</code></td><td><code>string</code></td><td>Original assignment, identity source, group mapping, matched permission path and rule, complete role restrictions, and raw item permissions. No portal bitmask is decoded into a table grant.</td></tr>
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
