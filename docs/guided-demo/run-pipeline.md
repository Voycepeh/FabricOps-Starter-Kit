# Run a Data Pipeline

Use `02_pipeline` as the main engineering notebook for a governed FabricOps data pipeline. This journey observes and records what happened: it reads source data, profiles the source, applies visible transformations, profiles the transformed target, writes governed target outputs, and registers metadata and lineage participation evidence.

`02_pipeline` is where users:

- select or use the relevant agreement context created earlier in the guided demo;
- keep source and target configuration visible in notebook cells;
- read from configured Fabric targets instead of relying on an attached default Lakehouse;
- apply transformation logic that reviewers can inspect;
- write governed target outputs; and
- automatically register profiling, catalogue, schema, and runtime source and target participation evidence.

Guardrail enforcement is covered separately in [Run a Data Pipeline with Guardrails](run-pipeline-with-guardrails.md).

## Recommended flow

```text
read source
→ profile and register source evidence
→ transform
→ profile and register target evidence
→ write target
```

1. Open `02_pipeline` after environment and agreement setup.
2. Review the source and target configuration.
3. Read the source DataFrame from the configured Fabric source target.
4. Profile and register the source DataFrame with `profile_and_register_dataframe(...)`.
5. Apply visible transformation logic in notebook cells.
6. Profile and register the target DataFrame with `profile_and_register_dataframe(...)`.
7. Write the target output to the configured Fabric target.
8. Review the metadata evidence created by the run.

A source profiling call uses `profile_role="source"`. A target profiling call uses `profile_role="target"`. Each profile-and-register step writes profile evidence, catalogue identity, schema fingerprint evidence, and one lineage participation event for the DataFrame supplied to that call.

## Minimal profiling example

```python
from fabricops_kit import profile_and_register_dataframe

profiled_df = profile_and_register_dataframe(
    df,
    profile_role="source",
    environment_name="dev",
    store_type="lakehouse",
    layer="raw",
    table_name="customers",
)
```

For very large DataFrames, users can explicitly limit only the rows used for frequency grouping while keeping the main profile and metadata registration based on the full supplied DataFrame:

```python
profiled_df = profile_and_register_dataframe(
    df,
    profile_role="source",
    environment_name="dev",
    store_type="lakehouse",
    layer="raw",
    table_name="customers",
    frequency_sample_rows=100_000,
    frequency_sample_seed=42,
)
```

This is a conceptual example. Use the source and target values configured by your `00_env_config`, agreement context, and `02_pipeline` notebook cells.

## What the pipeline records

One `profile_and_register_dataframe()` call creates or updates evidence across three metadata tables.

### `METADATA_DATA_CATALOGUE`

`METADATA_DATA_CATALOGUE` stores physical table and column identity snapshots. It does not store profiling statistics. One row is registered for each observed column.

Important identity fields are:

| Field | Conceptual meaning |
| ----- | ------------------ |
| `metadata_table_key` | Stable identity for the physical table location. |
| `metadata_column_key` | Stable identity for a column within that table. |
| `schema_fingerprint` | Identity for one observed version of the complete DataFrame schema. |

The physical table identity is based on values such as `environment_name`, `store_type`, `layer`, `schema_name`, and `table_name`. Catalogue rows include fields such as `metadata_table_key`, `metadata_column_key`, `schema_fingerprint`, `environment_name`, `store_type`, `layer`, `schema_name`, `table_name`, `column_name`, `data_type`, and standard audit fields.

### `METADATA_DATA_PROFILED`

`METADATA_DATA_PROFILED` stores one statistical profile row per eligible DataFrame column. It records the values observed during the profiling run.

The main evidence categories are:

- row counts;
- null counts and percentages;
- distinct counts and percentages;
- numeric summary statistics where applicable;
- `frequency_json`;
- schema fingerprint;
- profile timestamp; and
- runtime audit fields.

The catalogue answers: **What table and column is this?**

The profiled table answers: **What did the values in this column look like during this run?**

### `METADATA_DATA_LINEAGE`

`METADATA_DATA_LINEAGE` stores one table-level participation event for each profiling and registration call.

A source call records `profile_role = source`. A target call records `profile_role = target`.

The lineage row includes runtime context such as `activity_id`, `notebook_id`, `notebook_name`, `workspace_id`, `workspace_name`, `metadata_table_key`, `schema_fingerprint`, `profile_role`, `profiled_at`, `committed_by`, `environment_name`, and `metadata_lakehouse_name`.

Source and target participation records sharing the same notebook activity allow users to reconstruct which tables participated in the pipeline execution. This is runtime source and target participation evidence, not a separately written direct source-to-target edge.

## Simple end-to-end evidence example

```python
df = spark.createDataFrame(
    [
        (1, "Active"),
        (2, "Active"),
        (3, "Inactive"),
        (4, "Active"),
    ],
    ["customer_id", "status"],
)

profiled_df = profile_and_register_dataframe(
    df,
    profile_role="source",
    environment_name="dev",
    store_type="lakehouse",
    layer="raw",
    table_name="customers",
)
```

For the first observation of this illustrative schema and activity, the call records:

| Metadata table | Rows written or upserted | Purpose |
| -------------- | ------------------------ | ------- |
| `METADATA_DATA_CATALOGUE` | 2 rows, one for `customer_id` and one for `status` | Physical table and column identity snapshots, idempotently upserted by `metadata_table_key + metadata_column_key + schema_fingerprint`. |
| `METADATA_DATA_PROFILED` | 2 appended rows, one statistical profile row per column | Statistical and frequency evidence per column. |
| `METADATA_DATA_LINEAGE` | 1 row | Table-level source participation evidence, idempotently upserted by `lineage_event_id`. |

Generated key values are intentionally not shown here. Treat values such as `metadata_table_key`, `metadata_column_key`, and `schema_fingerprint` as stable identifiers produced by FabricOps from the observed context and schema. Later identical catalogue and lineage observations may update existing rows, while `METADATA_DATA_PROFILED` remains append-oriented run evidence.

## Frequency evidence per column

Frequency evidence is embedded in the `frequency_json` field of each `METADATA_DATA_PROFILED` row. By default, frequency distributions use the complete DataFrame. For very large DataFrames, users can explicitly limit only the rows used for frequency grouping with `frequency_sample_rows`.

This does not sample the entire profiling operation:

| Evidence or calculation | Data used |
| ----------------------- | --------- |
| Statistical profile | Always calculated from the full supplied DataFrame. |
| Schema fingerprint | Always calculated from the full supplied DataFrame schema. |
| Catalogue and lineage | Always registered from the full supplied DataFrame context. |
| Frequency distribution | Uses the full supplied DataFrame by default, or an explicit deterministic sample when requested. |

For a suitable low-cardinality column such as `status` with no sampling requested, the embedded JSON can look like this:

```json
{
  "source_row_count": 4,
  "profiled_row_count": 4,
  "profiled_non_null_count": 4,
  "sampling_applied": false,
  "sampling_method": null,
  "sampling_seed": null,
  "requested_sample_rows": null,
  "values": [
    {
      "value": "Active",
      "count": 3,
      "percent": 75.0,
      "rank": 1
    },
    {
      "value": "Inactive",
      "count": 1,
      "percent": 25.0,
      "rank": 2
    }
  ]
}
```

With explicit sampling, the frequency payload records the source row count, sampled row count, sampling method, seed, and requested sample size:

```json
{
  "source_row_count": 10000000,
  "profiled_row_count": 100000,
  "profiled_non_null_count": 99500,
  "sampling_applied": true,
  "sampling_method": "deterministic_random_limit",
  "sampling_seed": 42,
  "requested_sample_rows": 100000,
  "values": [
    {
      "value": "Active",
      "count": 74000,
      "percent": 74.37,
      "rank": 1
    }
  ]
}
```

Sampling is opt-in. The default remains full-data frequency profiling. When sampling is requested, the same seed provides reproducible selection for the same input execution conditions. Sampling is performed once per orchestrator call, and all eligible frequency columns use that same sampled DataFrame instead of taking repeated independent samples by column.

Automatic frequency selection uses the statistical profile that has already been calculated from the full supplied DataFrame. This keeps notebook orchestration safe by avoiding full frequency profiling for automatic columns above the default high-cardinality threshold.

Conceptually, the order is:

```text
full-data statistical profile
→ determine automatic eligible columns
→ skip columns above the cardinality threshold
→ optionally sample rows
→ calculate frequency distributions for remaining columns
```

A high-cardinality column does not become eligible merely because a sample contains fewer distinct values.

Key behavior:

- The default automatic threshold is 80% distinct among non-null values.
- Exactly 80% remains eligible.
- Above 80% is skipped for automatic frequency profiling.
- Explicit caller-selected frequency columns override the automatic threshold.
- `frequency_columns=[]` disables frequency profiling and leaves `frequency_json` null.
- `frequency_max_distinct_percent=None` disables the automatic high-cardinality threshold safeguard.

For an automatically skipped high-cardinality column, `frequency_json` contains structured JSON:

```json
{
  "status": "skipped",
  "reason": "high_cardinality",
  "distinct_percent": 100.0,
  "threshold_percent": 80.0,
  "message": "Frequency profiling skipped because distinct percentage exceeded 80%."
}
```

For an all-null automatic column, `frequency_json` uses a separate skip reason:

```json
{
  "status": "skipped",
  "reason": "no_non_null_values",
  "distinct_percent": null,
  "threshold_percent": 80.0,
  "message": "Frequency profiling skipped because the column contains no non-null values."
}
```

Structured JSON distinguishes an intentional safety skip from a missing value and remains machine-readable for notebooks, dashboards, and AI-assisted review.

## Schema evolution tracking

Schema evolution is tracked through three related identifiers:

| Identifier | Meaning |
| ---------- | ------- |
| `metadata_table_key` | Identifies the physical table. |
| `metadata_column_key` | Identifies a column within that table. |
| `schema_fingerprint` | Identifies one observed version of the complete table schema. |

The catalogue upsert identity is:

```text
metadata_table_key + metadata_column_key + schema_fingerprint
```

This means:

- the same physical table keeps one stable `metadata_table_key`;
- unchanged columns keep the same `metadata_column_key`;
- when the DataFrame schema changes, a new `schema_fingerprint` is produced;
- rows under the prior fingerprint remain as historical schema evidence; and
- rows under the new fingerprint represent the newly observed schema snapshot.

Initial schema:

```text
customer_id: bigint
status: string
```

Later schema:

```text
customer_id: bigint
status: string
country: string
```

Conceptual catalogue snapshots:

| metadata_table_key | metadata_column_key | schema_fingerprint | column_name | data_type |
| ------------------ | ------------------- | ------------------ | ----------- | --------- |
| TABLE_ABC | COLUMN_CUSTOMER_ID | SCHEMA_V1 | customer_id | bigint |
| TABLE_ABC | COLUMN_STATUS | SCHEMA_V1 | status | string |
| TABLE_ABC | COLUMN_CUSTOMER_ID | SCHEMA_V2 | customer_id | bigint |
| TABLE_ABC | COLUMN_STATUS | SCHEMA_V2 | status | string |
| TABLE_ABC | COLUMN_COUNTRY | SCHEMA_V2 | country | string |

Inferred change:

- Added columns: `country`
- Removed columns: none
- Changed data types: none

This enables users to:

- identify newly added columns;
- identify removed columns;
- identify changed Spark data types;
- determine when a new schema was first observed;
- determine which notebook and activity registered it; and
- compare historical schema snapshots for the same physical table.

The current model stores schema snapshots rather than an explicit parent-child schema version chain. Evolution order is inferred from schema fingerprints and audit timestamps.

## Summary

| Metadata table | Rows written or upserted for a two-column DataFrame | Purpose |
| -------------- | ------------------------------------------------ | ------- |
| `METADATA_DATA_CATALOGUE` | 2 upserted rows | Physical table and column identity snapshots. |
| `METADATA_DATA_PROFILED` | 2 appended rows | Statistical and frequency evidence per column. |
| `METADATA_DATA_LINEAGE` | 1 upserted row per source or target call | Runtime table participation evidence. |

Next, continue to [Run a Data Pipeline with Guardrails](run-pipeline-with-guardrails.md).

See also: [Templates](../notebook-templates-implementation-guide/index.md) and [List of DQ Rules](../reference/dq-rules/index.md).
