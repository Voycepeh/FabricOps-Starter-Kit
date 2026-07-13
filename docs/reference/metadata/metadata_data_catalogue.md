# METADATA_DATA_CATALOGUE

**Purpose:** Minimal column-profile contract for observed physical Fabric tables.

One row represents one profiled column. Numeric-only statistics are nullable for non-numeric columns. `frequency_json` is optional evidence for callers that calculate a top-N frequency profile. Existing physical `METADATA_DATA_CATALOGUE` tables must be recreated because this is an intentional breaking schema change.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | Catalogue evidence writers | Stable key identifying the physical table across environment, store type, layer, schema, and table context. |
| `metadata_column_key` | `string` | No | Catalogue evidence writers | Stable key identifying a specific column within the physical table. |
| `environment_name` | `string` | No | Catalogue evidence writers | FabricOps environment such as development, test, or production. |
| `store_type` | `string` | No | Catalogue evidence writers | Physical Fabric storage type, currently `lakehouse` or `warehouse`. |
| `layer` | `string` | No | Catalogue evidence writers | Pipeline or data architecture layer such as raw, bronze, silver, gold, or curated. |
| `schema_name` | `string` | Yes | Catalogue evidence writers | Physical schema when applicable; nullable because some lakehouse table contexts may not expose a separate schema. |
| `table_name` | `string` | No | Catalogue evidence writers | Physical table name that was profiled. |
| `column_name` | `string` | No | Catalogue evidence writers | Physical column name that was profiled. |
| `data_type` | `string` | No | Profiling functions | Observed source data type for the profiled column. |
| `row_count` | `long` | No | Profiling functions | Number of rows included in the profile calculation. |
| `non_null_count` | `long` | No | Profiling functions | Number of profiled rows where the column value was not null. |
| `null_count` | `long` | No | Profiling functions | Number of profiled rows where the column value was null. |
| `null_percent` | `double` | No | Profiling functions | Percentage of profiled rows where the column value was null. |
| `distinct_count` | `long` | No | Profiling functions | Number of distinct values observed for the column. |
| `distinct_percent` | `double` | No | Profiling functions | Percentage of profiled rows represented by distinct values. |
| `mean_value` | `double` | Yes | Profiling functions | Mean value for numeric columns; null when not applicable. |
| `stddev_value` | `double` | Yes | Profiling functions | Standard deviation for numeric columns; null when not applicable. |
| `min_value` | `string` | Yes | Profiling functions | Minimum observed value serialized as a string for ordered columns. |
| `percentile_25_value` | `double` | Yes | Profiling functions | Twenty-fifth percentile for numeric columns; null when not applicable. |
| `median_value` | `double` | Yes | Profiling functions | Median value for numeric columns; null when not applicable. |
| `percentile_75_value` | `double` | Yes | Profiling functions | Seventy-fifth percentile for numeric columns; null when not applicable. |
| `max_value` | `string` | Yes | Profiling functions | Maximum observed value serialized as a string for ordered columns. |
| `is_sampled` | `boolean` | No | Catalogue evidence writers | True when the caller supplied a sampled or filtered DataFrame rather than the complete intended dataset. |
| `frequency_json` | `string` | Yes | Profiling functions | Optional serialized top-N frequency profile produced from `profile_frequency_distribution` output. |
| `profiled_at` | `timestamp` | No | Profiling functions | Time the data profile was calculated. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Time the catalogue row was persisted. |

## Related function reference

- [`profile_dataframe`](../../api/reference/profile_dataframe.md)
- [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md)
- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
