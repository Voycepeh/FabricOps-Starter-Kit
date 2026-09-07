# METADATA_GUARDRAIL

Define the expectations the data used in the ETL pipeline should meet.

## Writer functions

* [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md)
* [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md)

## Used in Workflow Template

* [`01_governance`](../../notebook-templates.md) — Guardrail authoring

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One configured Guardrail rule revision for one exact Data Contract version and optional column identity.

**Primary key:** `guardrail_rule_id` + `guardrail_version`

**Relationships:**

`METADATA_DATA_CONTRACT` **(N → 1)**
via `contract_id` + `contract_version`

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `column_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 20 |
| Business columns | 12 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `guardrail_rule_id` | `string` | Stable identifier for the guardrail rule row. |
| `guardrail_version` | `integer` | Metadata Guardrail field `guardrail_version`. |
| `contract_id` | `string` | Stable identifier for the contract row. |
| `contract_version` | `integer` | Version recorded for the contract row. |
| `column_id` | `string` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `guardrail_type` | `string` | Guardrail family recorded for the row. |
| `rule_id` | `string` | Rule identity stored by the authoring workflow. |
| `rule_type` | `string` | Specific rule type recorded within the guardrail family. |
| `rule_parameters_json` | `string` | Serialized rule parameters stored for the guardrail row. |
| `severity` | `string` | Severity recorded for the guardrail intent or result. |
| `is_active` | `boolean` | Whether the row is currently active. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
