# METADATA_DATA_CATALOGUE

**Purpose:** Observed table and column profiles used for catalogue review and runtime comparisons.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | Catalogue evidence writers | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | No | Catalogue evidence writers | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `environment_name`. |
| `store_type` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `store_type`. |
| `layer` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `layer`. |
| `schema_name` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `schema_name`. |
| `table_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `table_name`. |
| `column_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `column_name`. |
| `data_type` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `data_type`. |
| `row_count` | `long` | No | Catalogue evidence writers | Metadata Data Catalogue field `row_count`. |
| `non_null_count` | `long` | No | Catalogue evidence writers | Metadata Data Catalogue field `non_null_count`. |
| `null_count` | `long` | No | Catalogue evidence writers | Metadata Data Catalogue field `null_count`. |
| `null_percent` | `double` | No | Catalogue evidence writers | Metadata Data Catalogue field `null_percent`. |
| `distinct_count` | `long` | No | Catalogue evidence writers | Metadata Data Catalogue field `distinct_count`. |
| `distinct_percent` | `double` | No | Catalogue evidence writers | Metadata Data Catalogue field `distinct_percent`. |
| `mean_value` | `double` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `mean_value`. |
| `stddev_value` | `double` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `stddev_value`. |
| `min_value` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `min_value`. |
| `percentile_25_value` | `double` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `percentile_25_value`. |
| `median_value` | `double` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `median_value`. |
| `percentile_75_value` | `double` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `percentile_75_value`. |
| `max_value` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `max_value`. |
| `is_sampled` | `boolean` | No | Catalogue evidence writers | Metadata Data Catalogue field `is_sampled`. |
| `frequency_json` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `frequency_json`. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |

## Related function reference

- [`profile_dataframe`](../../api/reference/profile_dataframe.md)
- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
