# METADATA_ENRICHMENT

Add business and governance context to the data.

## Writer functions

* [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)

## Used in Workflow Template

* [`01_governance`](../../notebook-templates.md) — Guardrail governance review

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One appended enrichment value for one table or column identity in one environment.

**Primary key:** `enrichment_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id` + `column_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 15 |
| Business columns | 7 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `enrichment_id` | `string` | Identifier stored for `enrichment_id`. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `column_id` | `string` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `enrichment_level` | `string` | Metadata Enrichment field `enrichment_level`. |
| `enrichment_type` | `string` | Enrichment type recorded for the row. |
| `value` | `string` | Metadata Enrichment field `value`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
