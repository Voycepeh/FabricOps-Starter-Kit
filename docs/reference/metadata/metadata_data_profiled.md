# METADATA_DATA_PROFILED

**Purpose:** Detailed per-column profiling evidence captured from a profiled dataset snapshot.

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `metadata_table_key` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe`, `fabricops_kit.pipeline.profile_and_register_dataframe._metadata_table_key` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe`, `fabricops_kit.pipeline.profile_and_register_dataframe._metadata_column_key` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Environment name recorded for the metadata row. |
| `store_type` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Configured Fabric store type recorded for the profiled dataset. |
| `layer` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Configured data layer recorded for the profiled dataset. |
| `schema_name` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Lakehouse or warehouse schema name recorded for the dataset when available. |
| `table_name` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Physical table name recorded for the metadata row. |
| `column_name` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Physical column name recorded for the metadata row. |
| `data_type` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Stable data type label recorded for the column. |
| `row_count` | `long` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed total row count in the profiled dataset snapshot. |
| `non_null_count` | `long` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed non-null value count for the column. |
| `null_count` | `long` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed null value count for the column. |
| `null_percent` | `double` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed null percentage for the column. |
| `distinct_count` | `long` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed distinct value count for the column. |
| `distinct_percent` | `double` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed distinct percentage for the column. |
| `mean_value` | `double` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed mean value for numeric columns when available. |
| `stddev_value` | `double` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed standard deviation for numeric columns when available. |
| `min_value` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed minimum value captured as text. |
| `percentile_25_value` | `double` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed 25th percentile for numeric columns when available. |
| `median_value` | `double` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed median value for numeric columns when available. |
| `percentile_75_value` | `double` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed 75th percentile for numeric columns when available. |
| `max_value` | `string` | [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md), `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe` | Observed maximum value captured as text. |
| `frequency_json` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe`, `fabricops_kit.pipeline.profile_and_register_dataframe._frequency_json_dataframe` | Serialized frequency distribution for the column when enabled. |
| `schema_fingerprint` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe`, `fabricops_kit.pipeline.profile_and_register_dataframe._schema_fingerprint` | Deterministic fingerprint for the observed or governed schema snapshot. |
| `profiled_at` | `timestamp` | `fabricops_kit.pipeline.profile_and_register_dataframe._canonical_profiled_dataframe`, `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Timestamp when the dataset profile snapshot was captured. |
| `_committed_by` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.pipeline.profile_and_register_dataframe._audit_literal_columns` | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md)
- [`widget_select_guardrail_target`](../../api/reference/widget_select_guardrail_target.md)
