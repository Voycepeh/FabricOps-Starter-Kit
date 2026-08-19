# METADATA_DATA_PROFILED

See the column-level profile metrics captured for a dataset snapshot.

## Model

**Grain:** One observed column in one profiling snapshot.

**Primary key:** `profile_id`

**Relationships:**

* `table_id` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). Many column profile snapshots can describe the same logical Catalogue table over time.
* `column_id` → `METADATA_DATA_CATALOGUE.column_id` (**N:1**). Many profile snapshots can describe the same logical Catalogue column over time.
* **1:1**: One logical column Profile has one corresponding frequency distribution. The distribution is stored separately and flattened into multiple physical Frequency rows to avoid a large JSON payload in the Profile row.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 27 |
| Business columns | 19 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `profile_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Identifier stored for `profile_id`. |
| `profile_snapshot_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Identifier stored for `profile_snapshot_id`. |
| `table_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Identifier for the accessed table or object. |
| `column_id` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Identifier stored for `column_id`. |
| `environment_name` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Environment name recorded for the metadata row. |
| `data_type` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Stable data type label recorded for the column. |
| `row_count` | `long` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed total row count in the profiled dataset snapshot. |
| `non_null_count` | `long` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed non-null value count for the column. |
| `null_count` | `long` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed null value count for the column. |
| `null_percent` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed null percentage for the column. |
| `distinct_count` | `long` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed distinct value count for the column. |
| `distinct_percent` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed distinct percentage for the column. |
| `mean_value` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed mean value for numeric columns when available. |
| `stddev_value` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed standard deviation for numeric columns when available. |
| `min_value` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed minimum value captured as text. |
| `percentile_25_value` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed 25th percentile for numeric columns when available. |
| `median_value` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed median value for numeric columns when available. |
| `percentile_75_value` | `double` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed 75th percentile for numeric columns when available. |
| `max_value` | `string` | [`profile_and_register_table`](../../api/reference/profile_and_register_table.md), `fabricops_kit.pipeline.profile_and_register_table._canonical_profiled_dataframe` | Observed maximum value captured as text. |
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
* [`widget_author_guardrails`](../../api/reference/widget_author_guardrails.md)
* [`widget_author_dq_rules`](../../api/reference/widget_author_dq_rules.md)
