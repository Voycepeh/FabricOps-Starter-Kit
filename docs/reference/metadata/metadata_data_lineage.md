# METADATA_DATA_LINEAGE

Shows which tables a pipeline reads and writes, so you can trace how data moves through FabricOps.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)
* [`pipeline_read`](../../api/reference/pipeline_read.md)

## Used in Workflow Template

* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Source read capability
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One table's participation as a source or target in a pipeline operation.

**Primary key:** `lineage_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

**Implementation details:** See which registered tables participated as sources and targets in pipeline activities; table_name records the name at the participation write while table_id remains stable. The current notebook's Lineage defines Data Contract resolution scope.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 13 |
| Business columns | 5 |
| Audit columns | 8 |

## Implemented schema

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr><td><code>lineage_id</code></td><td><code>string</code></td><td>Identifier stored for <code>lineage_id</code>.</td></tr>
<tr><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across environment, dataset, and table context.</td></tr>
<tr><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr><td><code>environment_name</code></td><td><code>string</code></td><td>Environment name recorded for the metadata row.</td></tr>
<tr><td><code>pipeline_role</code></td><td><code>string</code></td><td>Metadata Data Lineage field <code>pipeline_role</code>.</td></tr>
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
