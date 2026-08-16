# METADATA_SOURCE_OBSERVATION

**Purpose:** Append-only compact partition observations used for cheap pre-read source checking; each row links to METADATA_DATA_CATALOGUE through metadata_table_key.

## Grain

One partition row in one table observation.

## Primary key

`observation_id + partition_value`

## Foreign keys

- `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_key`
- `guardrail_rule_version_id` → `METADATA_GUARDRAIL.guardrail_rule_version_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 18 |
| Business columns | 10 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Key | Managed by | Description |
| --- | --- | --- | --- | --- |
| `observation_id` | `string` | **PK** | [`observe_table`](../../api/reference/observe_table.md) | Identifier stored for `observation_id`. |
| `metadata_table_key` | `string` | **FK** | [`observe_table`](../../api/reference/observe_table.md), `fabricops_kit.config.shared.build_metadata_table_key` | Canonical table identity shared with METADATA_DATA_CATALOGUE. |
| `guardrail_rule_version_id` | `string` | **FK** | [`observe_table`](../../api/reference/observe_table.md) | Identifier stored for `guardrail_rule_version_id`. |
| `environment_name` | `string` | **—** | [`observe_table`](../../api/reference/observe_table.md) | Environment name recorded for the metadata row. |
| `partition_value` | `string` | **PK** | [`observe_table`](../../api/reference/observe_table.md) | String representation of the observed partition value. |
| `row_count` | `long` | **—** | [`observe_table`](../../api/reference/observe_table.md) | Number of rows observed in the partition, or zero for a removal tombstone. |
| `min_change_value` | `string` | **—** | [`observe_table`](../../api/reference/observe_table.md) | Earliest observed change-column value, or null for a removal tombstone. |
| `max_change_value` | `string` | **—** | [`observe_table`](../../api/reference/observe_table.md) | Latest observed change-column value, or null for a removal tombstone. |
| `is_present` | `boolean` | **—** | [`observe_table`](../../api/reference/observe_table.md) | Whether the partition exists in this observation; false identifies a removal tombstone. |
| `observed_at` | `timestamp` | **—** | [`observe_table`](../../api/reference/observe_table.md) | Timestamp when FabricOps collected this compact source observation. |
| `_committed_by` | `string` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | **—** | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`observe_table`](../../api/reference/observe_table.md)
