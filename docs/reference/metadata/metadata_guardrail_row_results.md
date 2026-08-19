# METADATA_GUARDRAIL_ROW_RESULTS

See the individual records that failed a Data Quality rule.

## Model

**Grain:** One failed record belonging to one Guardrail Result.

**Primary key:** `guardrail_row_result_id`

**Relationships:**

* `guardrail_result_id` → `METADATA_GUARDRAIL_RESULTS.guardrail_result_id` (**N:1**). Many failed records can belong to one Guardrail Result.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 14 |
| Business columns | 6 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `guardrail_row_result_id` | `string` | `fabricops_kit.pipeline.shared.check_dq_runtime` | Identifier stored for `guardrail_row_result_id`. |
| `guardrail_result_id` | `string` | `fabricops_kit.pipeline.shared.check_dq_runtime` | Stable identifier for the runtime guardrail result row. |
| `row_identity` | `string` | `fabricops_kit.pipeline.shared.check_dq_runtime` | Metadata Guardrail Row Results field `row_identity`. |
| `involved_columns_json` | `string` | `fabricops_kit.pipeline.shared.check_dq_runtime` | JSON payload stored for `involved_columns_json`. |
| `failed_values_json` | `string` | `fabricops_kit.pipeline.shared.check_dq_runtime` | JSON payload stored for `failed_values_json`. |
| `failure_reason` | `string` | `fabricops_kit.pipeline.shared.check_dq_runtime` | Metadata Guardrail Row Results field `failure_reason`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

* [`check_dq`](../../api/reference/check_dq.md)
