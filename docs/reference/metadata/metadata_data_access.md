# METADATA_DATA_ACCESS

Records permissions observed for governed tables across Workspace, OneLake and SQL access. It does not determine a person's effective access.

## Writer functions

* [`scan_onelake_access`](../../api/reference/scan_onelake_access.md)
* [`scan_sql_access`](../../api/reference/scan_sql_access.md)
* [`scan_workspace_access`](../../api/reference/scan_workspace_access.md)

## Used in Workflow Template

* [`90_access_inventory (planned)`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Access inventory

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One observed permission for a principal or access selector on a table during one scan.

**Primary key:** `access_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

**Implementation details:** See observable Workspace, OneLake Security, and SQL access for registered governed physical tables across configured Fabric data items; table_name records the Catalogue name matched at scan time. This is not an effective-access resolver.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 24 |
| Business columns | 16 |
| Audit columns | 8 |

## Implemented schema

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr><td><code>access_id</code></td><td><code>string</code></td><td>Stable identifier for one observed SQL permission row.</td></tr>
<tr><td><code>user_principal</code></td><td><code>string</code></td><td>SQL principal name observed for the permission row.</td></tr>
<tr><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across environment, dataset, and table context.</td></tr>
<tr><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr><td><code>environment_name</code></td><td><code>string</code></td><td>Environment name recorded for the metadata row.</td></tr>
<tr><td><code>access_level</code></td><td><code>string</code></td><td>SQL permission class or scope, such as SCHEMA or OBJECT_OR_COLUMN.</td></tr>
<tr><td><code>access_value</code></td><td><code>string</code></td><td>SQL permission name, such as SELECT.</td></tr>
<tr><td><code>access_state</code></td><td><code>string</code></td><td>Observed SQL permission state, such as GRANT or DENY.</td></tr>
<tr><td><code>access_snapshot_id</code></td><td><code>string</code></td><td>Identifier grouping permission rows captured in the same access inventory snapshot.</td></tr>
<tr><td><code>user_type</code></td><td><code>string</code></td><td>SQL principal type observed for the permission row.</td></tr>
<tr><td><code>role_name</code></td><td><code>string</code></td><td>Database role through which the permission is inherited when applicable.</td></tr>
<tr><td><code>permission_source</code></td><td><code>string</code></td><td>Whether the observed permission is direct or inherited through a database role.</td></tr>
<tr><td><code>database_name</code></td><td><code>string</code></td><td>Database containing the observed permission scope.</td></tr>
<tr><td><code>schema_name</code></td><td><code>string</code></td><td>Lakehouse or warehouse schema name recorded for the dataset when available.</td></tr>
<tr><td><code>object_name</code></td><td><code>string</code></td><td>Database object name covered by the observed permission when applicable.</td></tr>
<tr><td><code>object_type</code></td><td><code>string</code></td><td>Database object type covered by the observed permission when applicable.</td></tr>
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
