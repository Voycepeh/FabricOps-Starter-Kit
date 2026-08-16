# METADATA_DATA_CATALOGUE

See the tables and columns FabricOps has registered, including where they live and how they are structured.

## Model

**Grain:** One registered column for one table and schema fingerprint in one environment.

**Primary key:** `environment_name` + `metadata_table_key` + `metadata_column_key` + `schema_fingerprint`

**Relationships:**

* **1:N**: One catalogue table identity can be referenced by many Source Observation, Data Profiled, Data Lineage, Enrichment and Guardrail rows.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 18 |
| Business columns | 10 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `metadata_table_key` | `string` | `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe`, `fabricops_kit.config.shared.build_metadata_table_key` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe`, `fabricops_kit.config.shared.build_metadata_column_key` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `schema_fingerprint` | `string` | `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe`, `fabricops_kit.pipeline.profile_and_register_table._schema_fingerprint` | Deterministic fingerprint for the observed or governed schema snapshot. |
| `environment_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Environment name recorded for the metadata row. |
| `store_type` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Configured Fabric store type recorded for the profiled dataset. |
| `layer` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | The configured medallion layer where the table is stored. |
| `schema_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Lakehouse or warehouse schema name recorded for the dataset when available. |
| `table_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Physical table name recorded for the metadata row. |
| `column_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Physical column name recorded for the metadata row. |
| `data_type` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Stable data type label recorded for the column. |
| `_committed_by` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

* [`profile_and_register_table`](../../api/reference/profile_and_register_table.md)
* [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
