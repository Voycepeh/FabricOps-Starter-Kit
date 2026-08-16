# METADATA_DATA_LINEAGE

See where the data came from and where it ends up.

## Model

**Grain:** One source or target participation event for one profiled table snapshot in one Fabric activity.

**Primary key:** `lineage_event_id`

**Relationships:**

* `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_table_key` (**N:1**). Many lineage events can refer to the same logical catalogue table identity.
* **1:N**: One lineage event can describe a table snapshot that is represented by many profiled column rows through metadata_table_key, schema_fingerprint and profiled_at.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 14 |
| Business columns | 6 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `lineage_event_id` | `string` | `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation`, `fabricops_kit.pipeline.profile_and_register_table._lineage_event_id` | Deterministic runtime lineage event identifier. |
| `metadata_table_key` | `string` | `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation`, `fabricops_kit.config.shared.build_metadata_table_key` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `schema_fingerprint` | `string` | `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation`, `fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint` | Deterministic fingerprint for the observed or governed schema snapshot. |
| `profile_role` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Whether the profiled dataset participated as a source or target. |
| `profiled_at` | `timestamp` | `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe`, `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Timestamp when the dataset profile snapshot was captured. |
| `environment_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._write_lineage_participation` | Environment name recorded for the metadata row. |
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
