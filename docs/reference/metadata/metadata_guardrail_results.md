# METADATA_GUARDRAIL_RESULTS

See whether the expectations of the data in the ETL pipeline run are met.

## Writer functions

* [`check_changes`](../../api/reference/check_changes.md)
* [`check_dq`](../../api/reference/check_dq.md)
* [`check_freshness`](../../api/reference/check_freshness.md)
* [`check_schema`](../../api/reference/check_schema.md)

## Model

**Grain:** One runtime outcome for one Guardrail rule in one pipeline run.

**Primary key:** `guardrail_result_id`

**Relationships:**

`METADATA_GUARDRAIL` **(N → 1)**
via `guardrail_rule_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 18 |
| Business columns | 10 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `guardrail_result_id` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Stable identifier for the runtime guardrail result row. |
| `guardrail_rule_id` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Stable identifier for the guardrail rule row. |
| `guardrail_version` | `integer` | [`check_schema`](../../api/reference/check_schema.md), [`check_freshness`](../../api/reference/check_freshness.md), [`check_changes`](../../api/reference/check_changes.md), [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Metadata Guardrail Results field `guardrail_version`. |
| `run_id` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Identifier stored for `run_id`. |
| `environment_name` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Environment name recorded for the metadata row. |
| `status` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Pipeline run status recorded with the run summary. |
| `can_continue` | `boolean` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Metadata Guardrail Results field `can_continue`. |
| `severity` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Severity recorded for the guardrail intent or result. |
| `reason` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Human-readable runtime reason recorded for the guardrail outcome. |
| `result_payload_json` | `string` | `fabricops_kit.pipeline.shared.write_guardrail_result_row`, `fabricops_kit.pipeline.shared.check_dq_runtime` | Serialized full runtime result payload written for the guardrail outcome. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |
