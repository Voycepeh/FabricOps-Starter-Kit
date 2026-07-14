# METADATA_DATA_CATALOGUE

**Purpose:** Observed table and column profiles used for catalogue review and runtime comparisons.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | Catalogue evidence writers | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | No | Catalogue evidence writers | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `schema_fingerprint` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `schema_fingerprint`. |
| `environment_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `environment_name`. |
| `store_type` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `store_type`. |
| `layer` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `layer`. |
| `schema_name` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `schema_name`. |
| `table_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `table_name`. |
| `column_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `column_name`. |
| `data_type` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `data_type`. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |

## Related function reference

- [`profile_dataframe`](../../api/reference/profile_dataframe.md)
- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
