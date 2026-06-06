# Pipeline Guardrails

`03_pc` owns pipeline guardrails. It pipes data from source to target, captures metadata, and enforces approved rules and classifications alongside schema and data drift guardrails.

Read [How FabricOps Works](how-fabricops-works/index.md) first for the full `01_da` → `03_pc` → `04_gov` → `03_pc` loop. This page focuses on the guardrail pattern inside `03_pc`.

Separate data contracts are not part of the current operating model. The checks that control pipeline behavior live in the relevant `03_pc` notebook and can use approved governance metadata from `04_gov` on later runs.

![Schema and data-change guardrails showing source and target validation flow](assets/fabricops-schema-data-guardrails.png){ .full-width }

## What `03_pc` owns

A `03_pc` notebook should make its guardrails explicit before writing outputs:

- schema validation for expected columns and datatypes;
- data-change monitoring for unusual row count, null, distinct, or distribution changes;
- approved data quality rules, sensitivity rules, and classification rules from governance review when the pipeline reads or implements them;
- notebook-defined DQ checks added where the pipeline logic lives;
- fail-fast behavior for blocking guardrail results;
- output writes only after required guardrails pass;
- profile and lineage metadata;
- run summaries for review.

`04_gov` adds reviewed metadata. After a person approves that metadata, `03_pc` can use the approved rules and classifications during later pipeline runs.

## Guardrail flow

Use the same pattern before transformation and before target publication:

1. validate the dataframe schema;
2. stop when the schema result is blocking;
3. profile the dataframe and compare it with the selected baseline;
4. stop when the data-change result is blocking;
5. apply approved governance metadata that the pipeline reads or implements;
6. run any notebook-defined DQ checks;
7. write outputs only after required guardrails pass;
8. record profile metadata, lineage, and run-summary metadata.

Warnings should remain visible without stopping execution. Monitor-only presets can be used when changes should be reviewed but should not block publication.

## Starter implementation pattern

```python
source_schema_result = validate_schema(
    dataframe=df_source,
    expected_schema=SOURCE_EXPECTED_SCHEMA,
    preset=SOURCE_SCHEMA_CHECK,
)

stop_if_failed(source_schema_result)

source_change_result = monitor_data_changes(
    spark=spark,
    dataframe=df_source,
    metadata_table=CATALOGUE_TABLE,
    dataset_name=DATASET_NAME,
    table_name=SOURCE_TABLE,
    stage="source",
    preset=SOURCE_DATA_CHANGE_CHECK,
    exclude_run_id=RUN_ID,
    policy_overrides=SOURCE_DATA_CHANGE_OVERRIDES,
)

stop_if_failed(source_change_result)
```

Apply the same pattern to the proposed target before writing:

```python
target_schema_result = validate_schema(
    dataframe=df_output,
    expected_schema=TARGET_EXPECTED_SCHEMA,
    preset=TARGET_SCHEMA_CHECK,
)

stop_if_failed(target_schema_result)

target_change_result = monitor_data_changes(
    spark=spark,
    dataframe=df_output,
    metadata_table=CATALOGUE_TABLE,
    dataset_name=DATASET_NAME,
    table_name=TARGET_TABLE,
    stage="target",
    preset=TARGET_DATA_CHANGE_CHECK,
    exclude_run_id=RUN_ID,
    policy_overrides=TARGET_DATA_CHANGE_OVERRIDES,
)

stop_if_failed(target_change_result)
```

## Recommended starter settings

```python
SOURCE_SCHEMA_CHECK = "allow_new_columns"
TARGET_SCHEMA_CHECK = "strict"

SOURCE_DATA_CHANGE_CHECK = "changing_data"
TARGET_DATA_CHANGE_CHECK = "changing_data"

SOURCE_DATA_CHANGE_OVERRIDES = {}
TARGET_DATA_CHANGE_OVERRIDES = {}

MARK_CURRENT_PROFILE_AS_APPROVED_BASELINE = False
```

## Schema presets

| Preset | Behavior |
| --- | --- |
| `strict` | Missing columns, datatype changes, and unexpected columns block execution. |
| `allow_new_columns` | Missing columns and datatype changes block. New columns are warnings. |
| `monitor_only` | All differences are reported without blocking. |

## Data-change presets

| Preset | Baseline | Can block |
| --- | --- | ---: |
| `changing_data` | Latest successful profile | Yes |
| `fixed_data` | Approved profile | Yes |
| `monitor_changing_data` | Latest successful profile | No |
| `monitor_fixed_data` | Approved profile | No |

Use `changing_data` for operational or transactional datasets. Use `fixed_data` for reference, historical, or controlled datasets that should remain stable.

## Metadata for review

`monitor_data_changes()` returns profile and comparison metadata that can be written to metadata tables:

| Property | Purpose |
| --- | --- |
| `profile` | Current profile dataframe ready for catalogue metadata. |
| `profile_payload` | Normalized profile used for comparison. |
| `baseline` | Selected historical profile, or `None`. |
| `result` | Guardrail status, checks, message, and `can_continue`. |

Together with lineage and run summaries, this metadata helps reviewers and support teams understand what the pipeline checked and why it did or did not write outputs.
