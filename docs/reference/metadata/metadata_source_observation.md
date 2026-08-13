# METADATA_SOURCE_OBSERVATION

**Purpose:** Append-only compact source-partition observations used for incremental read planning.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 21 |
| Business columns | 13 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `source_id` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Identifier stored for `source_id`. |
| `observation_definition_id` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Identifier stored for `observation_definition_id`. |
| `source_type` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `source_type`. |
| `source_target` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `source_target`. |
| `source_schema` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `source_schema`. |
| `source_table` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `source_table`. |
| `partition_value` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `partition_value`. |
| `is_present` | `boolean` | [`observe_source`](../../api/reference/observe_source.md) | Boolean state recorded for `is_present`. |
| `row_count` | `long` | [`observe_source`](../../api/reference/observe_source.md) | Observed total row count in the profiled dataset snapshot. |
| `observed_min` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `observed_min`. |
| `observed_max` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `observed_max`. |
| `fingerprint` | `string` | [`observe_source`](../../api/reference/observe_source.md) | Metadata Source Observation field `fingerprint`. |
| `observed_at` | `timestamp` | [`observe_source`](../../api/reference/observe_source.md) | Timestamp stored for `observed_at`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`observe_source`](../../api/reference/observe_source.md)
