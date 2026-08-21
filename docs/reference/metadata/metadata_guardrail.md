# METADATA_GUARDRAIL

Define the expectations the data used in the ETL pipeline should meet.

## Model

**Grain:** One configured Guardrail rule for one Catalogue table or column in one environment.

**Primary key:** `guardrail_rule_id` + `guardrail_version`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id` + `column_id`

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `guardrail_rule_id` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Stable identifier for the guardrail rule row. |
| `guardrail_version` | `integer` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Metadata Guardrail field `guardrail_version`. |
| `table_id` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Identifier for the accessed table or object. |
| `column_id` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Identifier stored for `column_id`. |
| `environment_name` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Environment name recorded for the metadata row. |
| `guardrail_type` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Guardrail family recorded for the row. |
| `rule_id` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Rule identity stored by the authoring workflow. |
| `rule_type` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Specific rule type recorded within the guardrail family. |
| `rule_parameters_json` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Serialized rule parameters stored for the guardrail row. |
| `severity` | `string` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Severity recorded for the guardrail intent or result. |
| `is_active` | `boolean` | `fabricops_kit.pipeline.shared.canonical_guardrail_rule_record` | Whether the row is currently active. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |
