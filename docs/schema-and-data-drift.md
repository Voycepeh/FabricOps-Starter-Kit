# Schema and data-change guardrails

FabricOps Starter Kit keeps the production notebook experience simple:

> Users choose intent through presets. FabricOps handles profiling, baseline selection, comparison and enforcement mechanics.

Use schema validation to confirm the dataframe shape you expect, and use data-change monitoring to compare current profile evidence with the right historical baseline. Keep the two checks separate so a schema issue is easy to explain separately from a distribution or row-count change.

## Beginner workflow

```python
source_schema_result = validate_schema(
    dataframe=df_source,
    expected_schema=SOURCE_EXPECTED_SCHEMA,
    preset=SOURCE_SCHEMA_CHECK,
)

source_change_result = monitor_data_changes(
    spark=spark,
    dataframe=df_source,
    metadata_table=CATALOGUE_TABLE,
    dataset_name=DATASET_NAME,
    table_name=SOURCE_TABLE,
    stage="source",
    preset=SOURCE_DATA_CHANGE_CHECK,
    exclude_run_id=RUN_ID,
)

stop_if_failed(source_schema_result)
stop_if_failed(source_change_result)
```

Apply the same pattern to the proposed target dataframe before publication:

```python
target_schema_result = validate_schema(
    dataframe=df_transformed,
    expected_schema=TARGET_EXPECTED_SCHEMA,
    preset=TARGET_SCHEMA_CHECK,
)

target_change_result = monitor_data_changes(
    spark=spark,
    dataframe=df_output,
    metadata_table=CATALOGUE_TABLE,
    dataset_name=DATASET_NAME,
    table_name=TARGET_TABLE,
    stage="target",
    preset=TARGET_DATA_CHANGE_CHECK,
    exclude_run_id=RUN_ID,
)

stop_if_failed(target_schema_result)
stop_if_failed(target_change_result)
```

## Schema presets

| Preset | Use when | Blocking behaviour |
| --- | --- | --- |
| `strict` | The dataframe must exactly match the expected schema. | Missing required columns, datatype changes, and unexpected new columns stop execution. |
| `allow_new_columns` | Upstream systems may add fields. | Missing required columns and datatype changes stop execution; unexpected columns are reported as warnings. |
| `monitor_only` | Schema changes should be visible but non-blocking. | All differences are reported and `can_continue=True`. |

## Data-change presets

| Preset | Baseline | Behaviour |
| --- | --- | --- |
| `changing_data` | Latest successful profile for the same dataset, table, and stage. | Uses moderate thresholds. Warnings continue; blocking drift stops publication. Successful observed profiles can become future baselines when evidence is written. |
| `fixed_data` | Approved profile for the same dataset, table, and stage. | Uses stricter thresholds. Blocking drift stops publication. It does not silently fall back to latest successful evidence. |
| `monitor_only` | Relevant latest successful baseline. | Loads a baseline, profiles, compares, and reports warnings without blocking execution. |

## Optional policy overrides

Advanced users can tune a preset without rebuilding the whole policy:

```python
source_change_result = monitor_data_changes(
    spark=spark,
    dataframe=df_source,
    metadata_table=CATALOGUE_TABLE,
    dataset_name=DATASET_NAME,
    table_name=SOURCE_TABLE,
    stage="source",
    preset="changing_data",
    policy_overrides={
        "block_numeric_psi": 0.30,
    },
)
```

Overrides are merged with the selected preset defaults.

## Profile evidence

`monitor_data_changes()` returns a wrapper with:

- `profile`: the current profile dataframe, ready to enrich and write as catalogue evidence;
- `profile_payload`: the normalized current profile used for comparison;
- `baseline`: the selected baseline profile, or `None` when no baseline exists;
- `result`: the standard guardrail result with `status`, `can_continue`, `checks`, and `message`.

Keep approved baseline promotion explicit. Setting `MARK_CURRENT_PROFILE_AS_APPROVED_BASELINE = True` in the notebook marks written evidence as approved; selecting `fixed_data` only chooses approved evidence for comparison.
