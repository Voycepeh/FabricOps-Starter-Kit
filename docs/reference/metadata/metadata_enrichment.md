# METADATA_ENRICHMENT

Add business and governance context to the data.

## Model

**Grain:** One appended enrichment value for one table or column identity in one environment.

**Primary key:** `enrichment_id`

**Relationships:**

* `table_id` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Many table- or column-level enrichment rows can reference the same logical Catalogue table identity in an environment.
* `column_id` → `METADATA_DATA_CATALOGUE.column_id` (**N:1**). Column-level enrichment references the Catalogue column through column_id while retaining its parent table_id; table-level enrichment leaves column_id empty.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 15 |
| Business columns | 7 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `enrichment_id` | `string` | `fabricops_kit.widgets.enrichment_shared.build_enrichment_records` | Identifier stored for `enrichment_id`. |
| `table_id` | `string` | `fabricops_kit.widgets.enrichment_shared.build_enrichment_records` | Identifier for the accessed table or object. |
| `column_id` | `string` | `fabricops_kit.widgets.enrichment_shared.build_enrichment_records` | Identifier stored for `column_id`. |
| `environment_name` | `string` | `fabricops_kit.widgets.enrichment_shared.build_enrichment_records` | Environment name recorded for the metadata row. |
| `enrichment_level` | `string` | `fabricops_kit.widgets.enrichment_shared.build_enrichment_records` | Metadata Enrichment field `enrichment_level`. |
| `enrichment_type` | `string` | `fabricops_kit.widgets.enrichment_shared.build_enrichment_records` | Enrichment type recorded for the row. |
| `value` | `string` | `fabricops_kit.widgets.enrichment_shared.build_enrichment_records` | Metadata Enrichment field `value`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Breaking pre release replacement

This intentionally breaking schema replaces the previous enrichment lifecycle and payload model. Existing development `METADATA_ENRICHMENT` tables must be recreated; no automated migration or compatibility support is provided. Values to retain may be exported and manually reshaped before recreation.

## Current value

The latest appended row for `enrichment_level` + `metadata_key` + `enrichment_type` is current, ordered by `_committed_at`, `_activity_id`, and `enrichment_id`. Empty values are rejected, so clearing is deferred to a future change.

## Examples

| enrichment_level | metadata_key | enrichment_type | value |
| --- | --- | --- | --- |
| table | tbl_abc | Description | Student enrolment records |
| table | tbl_abc | Classification | Highly sensitive |
| column | col_xyz | Description | Unique student identifier |
| column | col_xyz | Personal_identifier | Direct PII |

The catalogue remains the source of table and column identity. New enrichment types do not require a schema change.

## Related function reference

* [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
