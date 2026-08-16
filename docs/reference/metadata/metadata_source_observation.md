# METADATA_SOURCE_OBSERVATION

See whether the source arrived and changed as expected.

## Model

**Grain:** One observed partition state for one source table at one observation time.

**Primary key:** `metadata_table_key` + `partition_column` + `partition_value` + `observed_at`

**Relationships:**

* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many source partition observations can belong to one logical catalogue table identity.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 20 |
| Business columns | 12 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `metadata_table_key` | `string` | [`observe_table`](../../api/reference/observe_table.md), `fabricops_kit.config.shared.build_metadata_table_key` | Canonical table identity shared with METADATA_DATA_CATALOGUE. |
| `source_target` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Logical FabricOps target resolved through 00_env_config. |
| `source_schema` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Resolved physical source schema when the configured store uses one. |
| `source_table` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Resolved physical source table name. |
| `partition_column` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Column whose distinct values define observed source partitions. |
| `partition_value` | `string` | [`observe_table`](../../api/reference/observe_table.md) | String representation of the observed partition value. |
| `change_column` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Trustworthy source column used for automatic minimum and maximum evidence. |
| `row_count` | `long` | [`observe_table`](../../api/reference/observe_table.md) | Number of rows observed in the partition, or zero for a removal tombstone. |
| `min_change_value` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Earliest observed change-column value, or null for a removal tombstone. |
| `max_change_value` | `string` | [`observe_table`](../../api/reference/observe_table.md) | Latest observed change-column value, or null for a removal tombstone. |
| `is_present` | `boolean` | [`observe_table`](../../api/reference/observe_table.md) | Whether the partition exists in this observation; false identifies a removal tombstone. |
| `observed_at` | `timestamp` | [`observe_table`](../../api/reference/observe_table.md) | Timestamp when FabricOps collected this compact source observation. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

* [`observe_table`](../../api/reference/observe_table.md)
