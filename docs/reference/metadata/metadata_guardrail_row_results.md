# METADATA_GUARDRAIL_ROW_RESULTS

**Purpose:** Failed source-row and failed-DQ-rule evidence linked to runtime guardrail outcomes.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 22 |
| Business columns | 14 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `guardrail_row_result_id` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Identifier stored for `guardrail_row_result_id`. |
| `guardrail_result_id` | `string` | `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Stable identifier for the runtime guardrail result row. |
| `guardrail_rule_id` | `string` | `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Stable identifier for the guardrail rule row. |
| `metadata_table_key` | `string` | `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime`, `fabricops_kit.config.shared.build_metadata_table_key` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Environment name recorded for the metadata row. |
| `dataset_name` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Dataset name recorded for the metadata row. |
| `table_name` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Physical table name recorded for the metadata row. |
| `row_identity` | `string` | `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Metadata Guardrail Row Results field `row_identity`. |
| `rule_type` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Specific rule type recorded within the guardrail family. |
| `involved_columns_json` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | JSON payload stored for `involved_columns_json`. |
| `failed_values_json` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | JSON payload stored for `failed_values_json`. |
| `rule_details_json` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | JSON payload stored for `rule_details_json`. |
| `failure_reason` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Metadata Guardrail Row Results field `failure_reason`. |
| `run_id` | `string` | [`check_dq`](../../api/reference/check_dq.md), `fabricops_kit.pipeline.guardrails_shared.check_dq_runtime` | Identifier stored for `run_id`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`check_dq`](../../api/reference/check_dq.md)
