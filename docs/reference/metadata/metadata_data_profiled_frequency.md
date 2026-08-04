# METADATA_DATA_PROFILED_FREQUENCY

**Purpose:** Flattened distinct-value frequency rows joined to compact profile summaries through metadata_column_key.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 16 |
| Business columns | 8 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `metadata_column_key` | `string` | `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `value` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md) | Metadata Data Profiled Frequency field `value`. |
| `frequency_count` | `long` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md) | Metadata Data Profiled Frequency field `frequency_count`. |
| `frequency_percent` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md) | Metadata Data Profiled Frequency field `frequency_percent`. |
| `frequency_rank` | `integer` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md) | Metadata Data Profiled Frequency field `frequency_rank`. |
| `profiled_row_count` | `long` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md) | Metadata Data Profiled Frequency field `profiled_row_count`. |
| `profiled_non_null_count` | `long` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md) | Metadata Data Profiled Frequency field `profiled_non_null_count`. |
| `profiled_at` | `timestamp` | `fabricops_kit.pipeline.profile_and_register_table._frequency_metadata_dataframe`, `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Timestamp when the dataset profile snapshot was captured. |
| `_committed_by` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.pipeline.profile_and_register_table._audit_literal_columns` | Fabric execution activity identifier for the current notebook or pipeline run. |
