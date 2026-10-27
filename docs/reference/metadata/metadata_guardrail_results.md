# METADATA_GUARDRAIL_RESULTS

Summarizes Guardrail checks from finalized Test runs and Live runs, including whether execution could continue. It does not store failed business rows.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)

## Used in Workflow Template

* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One saved Guardrail outcome for an exact Data Contract version; Test outcomes are committed at explicit finalization.

**Primary key:** `guardrail_result_id`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → 1)**
via `run_id`

`METADATA_DATA_CONTRACT` **(N → 1)**
via `contract_id` + `contract_version`

**Implementation details:** Store aggregate Guardrail summaries for exact participating contract versions, captured table name, readable rule context, and continuation decisions; caller-owned failed business rows are not persisted here. Captured context does not follow later table or rule changes.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">27</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">19</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>guardrail_result_id</code></td><td><code>string</code></td><td>Stable identifier for the aggregate Guardrail result row.</td></tr>
<tr class="metadata-column--engineering"><td><code>guardrail_rule_id</code></td><td><code>string</code></td><td>Stable authored Guardrail identifier, or the synthetic completion-record identifier when rule_type is contract_validation.</td></tr>
<tr class="metadata-column--engineering"><td><code>guardrail_version</code></td><td><code>integer</code></td><td>Metadata Guardrail Results field <code>guardrail_version</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--engineering"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--engineering"><td><code>contract_id</code></td><td><code>string</code></td><td>Stable identifier for the contract row.</td></tr>
<tr class="metadata-column--engineering"><td><code>contract_version</code></td><td><code>integer</code></td><td>Version recorded for the contract row.</td></tr>
<tr class="metadata-column--engineering"><td><code>execution_type</code></td><td><code>string</code></td><td>Whether the runtime record came from Testing or Live contract execution. Testing results remain in memory; Live appends Guardrail Results. Historical validate records remain readable.</td></tr>
<tr class="metadata-column--engineering"><td><code>run_id</code></td><td><code>string</code></td><td>Identifier stored for <code>run_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>status</code></td><td><code>string</code></td><td>Pipeline run status recorded with the run summary.</td></tr>
<tr class="metadata-column--engineering"><td><code>can_continue</code></td><td><code>boolean</code></td><td>Metadata Guardrail Results field <code>can_continue</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>severity</code></td><td><code>string</code></td><td>Severity recorded for a Guardrail result.</td></tr>
<tr class="metadata-column--engineering"><td><code>guardrail_type</code></td><td><code>string</code></td><td>Guardrail family recorded for the row.</td></tr>
<tr class="metadata-column--engineering"><td><code>rule_id</code></td><td><code>string</code></td><td>Rule identity stored by the authoring workflow.</td></tr>
<tr class="metadata-column--engineering"><td><code>rule_type</code></td><td><code>string</code></td><td>Specific rule type recorded within the guardrail family.</td></tr>
<tr class="metadata-column--engineering"><td><code>action</code></td><td><code>string</code></td><td>Warn or Block action applied when an authored Guardrail fails.</td></tr>
<tr class="metadata-column--engineering"><td><code>reason</code></td><td><code>string</code></td><td>Human-readable reason recorded for the Guardrail outcome.</td></tr>
<tr class="metadata-column--engineering"><td><code>result_payload_json</code></td><td><code>string</code></td><td>Serialized aggregate result payload written for the Guardrail outcome.</td></tr>
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
