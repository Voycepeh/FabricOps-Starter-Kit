# METADATA_DATA_LINEAGE

See where the data came from and where it ends up.

## Model

**Grain:** One table participating as a source or target in one pipeline/profiling execution.

**Primary key:** `lineage_id`

**Relationships:**

* `table_id` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Many lineage participation records can refer to the same logical Catalogue table identity.
* `profile_snapshot_id` → `METADATA_DATA_PROFILED.profile_snapshot_id` (**N:1**). The lineage participation is recorded for the same profiling execution identified by profile_snapshot_id.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 13 |
| Business columns | 5 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `lineage_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Identifier stored for `lineage_id`. |
| `table_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Identifier for the accessed table or object. |
| `profile_snapshot_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Identifier stored for `profile_snapshot_id`. |
| `environment_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Environment name recorded for the metadata row. |
| `pipeline_role` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Metadata Data Lineage field `pipeline_role`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

* [`profile_and_register_table`](../../api/reference/profile_and_register_table.md)
