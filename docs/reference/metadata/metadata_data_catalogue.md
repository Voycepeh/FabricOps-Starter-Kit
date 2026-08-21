# METADATA_DATA_CATALOGUE

The current structural registry of known table and column assets.

## Model

**Grain:** One table or column asset in one environment.

**Primary key:** `environment_name` + `table_id` + `column_id`

**Relationships:**

* **1:N**: A Catalogue table identity can be referenced by many Profile, Lineage, Source Observation, Enrichment, Access and Guardrail rows over time.
* **1:N**: table_id identifies the logical table; column_id identifies a logical column while its normalized column name remains the same.
* **1:N**: data_type stores the current structural datatype and is_active indicates whether the asset currently exists. Datatype changes retain column_id, removed columns become inactive instead of being deleted, and a returning column with the same normalized name reuses its identity.
* **1:N**: METADATA_DATA_PROFILED retains the historical observations for Catalogue assets.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 21 |
| Business columns | 13 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `metadata_level` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Metadata Data Catalogue field `metadata_level`. |
| `table_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Identifier for the accessed table or object. |
| `column_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Identifier stored for `column_id`. |
| `environment_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Environment name recorded for the metadata row. |
| `store_type` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Configured Fabric store type recorded for the profiled dataset. |
| `layer` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | The configured medallion layer where the table is stored. |
| `schema_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Lakehouse or warehouse schema name recorded for the dataset when available. |
| `table_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Physical table name recorded for the metadata row. |
| `column_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Physical column name recorded for the metadata row. |
| `data_type` | `string` | `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Stable data type label recorded for the column. |
| `first_profiled_at` | `timestamp` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Timestamp stored for `first_profiled_at`. |
| `last_profiled_at` | `timestamp` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Timestamp stored for `last_profiled_at`. |
| `is_active` | `boolean` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Whether the row is currently active. |
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
