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
    policy_overrides=SOURCE_DATA_CHANGE_OVERRIDES,
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
    policy_overrides=TARGET_DATA_CHANGE_OVERRIDES,
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

Presets determine baseline and enforcement behaviour. Overrides adjust thresholds only.

| Preset | Baseline | Can block |
| --- | --- | ---: |
| `changing_data` | Latest successful profile | Yes |
| `fixed_data` | Approved profile | Yes |
| `monitor_changing_data` | Latest successful profile | No |
| `monitor_fixed_data` | Approved profile | No |

### `changing_data`

Use for operational or transactional data that changes regularly.

Default behaviour:

- Compare with the latest successful profile.
- Row count may change by up to 50%.
- Null percentage may change by up to 20 percentage points.
- Distinct percentage may change by up to 30 percentage points.
- Numeric PSI warns at 0.10 and blocks at 0.25.
- Categorical distance warns at 0.10 and blocks at 0.25.
- Blocking drift stops publication.

### `fixed_data`

Use for reference, historical, or controlled data that should remain stable.

Default behaviour:

- Compare with an approved baseline.
- Any row-count, null-rate, or distinct-rate change is treated strictly.
- Numeric PSI warns at 0.01 and blocks at 0.10.
- Categorical distance warns at 0.01 and blocks at 0.10.
- Blocking drift stops publication.
- The current profile does not automatically replace the approved baseline.

### `monitor_changing_data`

Use when operational or transactional changes should be reported without blocking.

Default behaviour:

- Compare with the latest successful profile.
- Use the same thresholds as `changing_data`.
- Always return `can_continue=True`.

### `monitor_fixed_data`

Use when reference, historical, or controlled data should be compared with an approved baseline without blocking.

Default behaviour:

- Compare with an approved baseline.
- Use the same thresholds as `fixed_data`.
- Always return `can_continue=True`.

## Optional policy overrides

Advanced users can tune thresholds without rebuilding the whole policy. An empty dictionary uses the preset unchanged:

```python
SOURCE_DATA_CHANGE_CHECK = "changing_data"

SOURCE_DATA_CHANGE_OVERRIDES = {
    # Leave empty to use FabricOps defaults.
    # "block_numeric_psi": 0.30,
    # "max_row_count_change_percent": 75,
}
```

Overrides are merged internally with the selected preset defaults:

```python
effective_policy = {
    **preset_defaults,
    **policy_overrides,
}
```

For example, override only the values your pipeline needs:

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

## Profile evidence

`monitor_data_changes()` returns a wrapper with:

- `profile`: the current profile dataframe, ready to enrich and write as catalogue evidence;
- `profile_payload`: the normalized current profile used for comparison;
- `baseline`: the selected baseline profile, or `None` when no baseline exists;
- `result`: the standard guardrail result with `status`, `can_continue`, `checks`, and `message`.

Keep approved baseline promotion explicit. Setting `MARK_CURRENT_PROFILE_AS_APPROVED_BASELINE = True` in the notebook marks written evidence as approved; selecting `fixed_data` or `monitor_fixed_data` only chooses approved evidence for comparison.
