# METADATA_DATA_CONTRACT

Defines what a table means, how it should be processed, which Guardrails apply and when it should be profiled. Frozen versions can be reused but not changed.

## Writer functions

* [`widget_data_contract`](../../api/reference/widget_data_contract.md)

## Used in Workflow Template

* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Data Contract authoring

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One Draft or Frozen version of a Data Contract for a table.

**Primary key:** `contract_id` + `contract_version`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → M)**
via Not defined in the current implementation.

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

**Implementation details:** Reusable immutable frozen table definition with Enrichment, executable Guardrails and independent profiling policies. Agreement linkage belongs to Activated Pipeline.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 15 |
| Business columns | 7 |
| Audit columns | 8 |

## Implemented schema

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr><td><code>contract_id</code></td><td><code>string</code></td><td>Stable identifier for the contract row.</td></tr>
<tr><td><code>contract_version</code></td><td><code>integer</code></td><td>Version recorded for the contract row.</td></tr>
<tr><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across environment, dataset, and table context.</td></tr>
<tr><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr><td><code>environment_name</code></td><td><code>string</code></td><td>Environment name recorded for the metadata row.</td></tr>
<tr><td><code>contract_payload_json</code></td><td><code>string</code></td><td>String column containing the JSON definition for this exact table/contract version and authoring environment, including Enrichment, Guardrails, and Processing; editable while draft and immutable once frozen. This is not a separate physical table.</td></tr>
<tr><td><code>status</code></td><td><code>string</code></td><td>Pipeline run status recorded with the run summary.</td></tr>
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
