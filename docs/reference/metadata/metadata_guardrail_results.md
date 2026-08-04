# METADATA_GUARDRAIL_RESULTS

**Purpose:** Runtime guardrail outcomes written by pipeline enforcement.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 26 |
| Business columns | 18 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `guardrail_result_id` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Stable identifier for the runtime guardrail result row. |
| `guardrail_rule_id` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Stable identifier for the guardrail rule row. |
| `result_id` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Stable identifier for the runtime result payload. |
| `rule_key` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Stable key used to group lifecycle versions of the same guardrail or enrichment rule. |
| `metadata_table_key` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row`, `fabricops_kit.config.metadata_keys._build_metadata_table_key` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Environment name recorded for the metadata row. |
| `dataset_name` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Dataset name recorded for the metadata row. |
| `table_name` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Physical table name recorded for the metadata row. |
| `column_name` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Physical column name recorded for the metadata row. |
| `guardrail_type` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Guardrail family recorded for the row. |
| `rule_type` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Specific rule type recorded within the guardrail family. |
| `status` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Pipeline run status recorded with the run summary. |
| `can_continue` | `boolean` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Metadata Guardrail Results field `can_continue`. |
| `severity` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Severity recorded for the guardrail intent or result. |
| `reason` | `string` | [`run_table_guardrails`](../../api/reference/run_table_guardrails.md), `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Human-readable runtime reason recorded for the guardrail outcome. |
| `expected_value_json` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Serialized expected value payload for the guardrail outcome. |
| `actual_value_json` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Serialized actual value payload for the guardrail outcome. |
| `result_payload_json` | `string` | `fabricops_kit.pipeline.metadata_evidence._write_guardrail_result_row` | Serialized full runtime result payload written for the guardrail outcome. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- [`display_guardrail_results`](../../api/reference/display_guardrail_results.md)
