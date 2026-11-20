# METADATA_DATA_LINEAGE

Records TABLE and FILE source/target participation within a Fabric Activity.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)

## Used in Workflow Template

* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One asset identity and role within one Fabric Activity.

**Primary key:** `workspace_id` + `lineage_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `workspace_id` + `table_id` + `asset_type`

**Implementation details:** Before saving new participation, FabricOps verifies one active physical Catalogue asset. asset_type is TABLE or FILE. table_id identifies either asset type; historical null asset_type rows with table_id remain TABLE. Released table lineage hashes are unchanged; file hashes include the FILE discriminator, the existing file identity value, Activity ID and role. Successful file operations persist participation before returning, independently of finalization. asset_name retains store/Files/relative_path for FILE participation. New rows use the resolved physical workspace in workspace_id and the notebook workspace in the audit fields. Run ID remains in METADATA_PIPELINE_RUN; its _activity_id correlates the same Fabric activity. Participation does not prove exact DataFrame dependencies or create transformation edges; table_name records the name at the participation write while table_id remains stable. The current notebook's Lineage defines Data Contract resolution scope.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">15</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">7</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>lineage_id</code></td><td><code>string</code></td><td>Identifier stored for <code>lineage_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>asset_type</code></td><td><code>string</code></td><td>Explicit asset discriminator: TABLE or FILE. Historical null values with table_id are TABLE.</td></tr>
<tr class="metadata-column--engineering"><td><code>asset_name</code></td><td><code>string</code></td><td>Human-readable asset reference captured at participation time; files retain store/Files/relative_path.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Common operational asset key for TABLE or FILE assets across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_role</code></td><td><code>string</code></td><td>Participation role: source for a Read or target for a Write.</td></tr>
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

## Automatic column cleanup

`setup_metadata_tables()` removes only the explicitly retired columns below. It preserves canonical rows, all eight audit columns and other extension columns. If a populated value cannot be proved redundant, setup fails for this table with data preserved.

| Retired column | Removal condition |
| --- | --- |
| `lineage_event_id` | Every value is SQL NULL |
| `profile_role` | Every value is SQL NULL |
| `profiled_at` | SQL NULL or equal to `_committed_at` |
| `recorded_at` | SQL NULL or equal to `_committed_at` |
| `source_id` | SQL NULL or equal to `table_id` |

See [`setup_metadata_tables`](../../api/reference/setup_metadata_tables.md) for transaction results and the Delta recovery boundary.
