# METADATA_ENRICHMENT

Add business and governance context to the data.

## Model

**Grain:** One appended enrichment value for one table or column identity in one environment.

**Primary key:** `enrichment_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id` + `column_id`

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
