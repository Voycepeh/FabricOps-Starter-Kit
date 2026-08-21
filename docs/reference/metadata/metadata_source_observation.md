# METADATA_SOURCE_OBSERVATION

See what FabricOps previously observed about the source data.

## Writer functions

* [`observe_table`](../../api/reference/observe_table.md)

## Related templates / solutions

* [`02_pipeline`](../../notebook-templates.md) — Source guardrails

## Model

**Grain:** One partition observation within one source-table observation.

**Primary key:** `observation_id` + `partition_value`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 16 |
| Business columns | 8 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `observation_id` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Identifier stored for `observation_id`. |
| `table_id` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Identifier for the accessed table or object. |
| `environment_name` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Environment name recorded for the metadata row. |
| `partition_value` | `string` | [`observe_table`](../../api/reference/observe_table.md) | String representation of the observed partition value. |
| `row_count` | `long` | [`observe_table`](../../api/reference/observe_table.md) | Number of rows observed in the partition, or zero for a removal tombstone. |
| `min_change_value` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Earliest observed change-column value, or null for a removal tombstone. |
| `max_change_value` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Latest observed change-column value, or null for a removal tombstone. |
| `is_present` | `boolean` | [`observe_table`](../../api/reference/observe_table.md) | Whether the partition exists in this observation; false identifies a removal tombstone. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |
