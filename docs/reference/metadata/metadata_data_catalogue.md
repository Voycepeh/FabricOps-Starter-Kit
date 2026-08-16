# METADATA_DATA_CATALOGUE

**Purpose:** Maintain the stable table and column identities that connect FabricOps metadata.

## Grain

One logical table or column asset.

## Primary key

`metadata_key`

## Foreign keys

- `metadata_table_key` → `METADATA_DATA_CATALOGUE.metadata_key (column rows)`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 20 |
| Business columns | 12 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Key | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_key` | `string` | **PK** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Metadata Data Catalogue field `metadata_key`. |
| `metadata_level` | `string` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Metadata Data Catalogue field `metadata_level`. |
| `metadata_table_key` | `string` | **FK** | `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe`, `fabricops_kit.config.shared.build_metadata_table_key` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe`, `fabricops_kit.config.shared.build_metadata_column_key` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `store_type` | `string` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Configured Fabric store type recorded for the profiled dataset. |
| `layer` | `string` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | The configured medallion layer where the table is stored. |
| `schema_name` | `string` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Lakehouse or warehouse schema name recorded for the dataset when available. |
| `table_name` | `string` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Physical table name recorded for the metadata row. |
| `column_name` | `string` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Physical column name recorded for the metadata row. |
| `first_profiled_at` | `timestamp` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Timestamp stored for `first_profiled_at`. |
| `last_profiled_at` | `timestamp` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Timestamp stored for `last_profiled_at`. |
| `is_active` | `boolean` | **—** | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._catalogue_dataframe_from_profiled` | Whether the row is currently active. |
| `_committed_by` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | **—** | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`profile_and_register_table`](../../api/reference/profile_and_register_table.md)
- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
