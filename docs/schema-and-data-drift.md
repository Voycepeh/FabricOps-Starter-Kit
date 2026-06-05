# Schema and data-change guardrails

![Schema and data-change guardrails showing source and target validation flow](assets/fabricops-schema-data-guardrails.png){ .full-width }

**FabricOps applies the same guardrail pattern before transformation and before target publication.**

At each stage:

Validate the dataframe schema.
Stop when the schema result is blocking.
Profile the dataframe and compare it with the preset-selected baseline.
Stop when the data-change result is blocking.
Continue to the next pipeline step.

The three public functions keep the notebook workflow simple:

- validate_schema() checks expected columns and datatypes.
- monitor_data_changes() handles profiling, baseline selection, and comparison.
- stop_if_failed() stops execution only when can_continue=False.

Warnings remain visible without stopping execution. Monitor-only presets always allow the pipeline to continue.

Beginner workflow

## Beginner workflow

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

| Preset              | Behaviour                                                                  |
| ------------------- | -------------------------------------------------------------------------- |
| `strict`            | Missing columns, datatype changes, and unexpected columns block execution. |
| `allow_new_columns` | Missing columns and datatype changes block. New columns are warnings.      |
| `monitor_only`      | All differences are reported without blocking.                             |

## Data-change presets

| Preset                  | Baseline                  | Can block |
| ----------------------- | ------------------------- | --------: |
| `changing_data`         | Latest successful profile |       Yes |
| `fixed_data`            | Approved profile          |       Yes |
| `monitor_changing_data` | Latest successful profile |        No |
| `monitor_fixed_data`    | Approved profile          |        No |

Use `changing_data` for operational or transactional datasets.

Use `fixed_data` for reference, historical, or controlled datasets that should remain stable.

Use the monitor variants when changes should be visible without stopping publication.

## Baseline behaviour

Changing-data presets compare with the latest successful matching profile.

Fixed-data presets compare only with an approved matching profile.

Selecting `fixed_data` does not approve the current profile. Baseline approval remains explicit:

```python
MARK_CURRENT_PROFILE_AS_APPROVED_BASELINE = True
```

Routine production runs should normally leave this set to `False`.

## Optional threshold overrides

Presets control baseline selection and blocking behaviour. Overrides adjust thresholds only.

```python
SOURCE_DATA_CHANGE_OVERRIDES = {
    "block_numeric_psi": 0.30,
    "max_row_count_change_percent": 75,
}
```

An empty dictionary uses the preset defaults unchanged.

## Returned evidence

`monitor_data_changes()` returns:

| Property          | Purpose                                                 |
| ----------------- | ------------------------------------------------------- |
| `profile`         | Current profile dataframe ready for catalogue evidence. |
| `profile_payload` | Normalized profile used for comparison.                 |
| `baseline`        | Selected historical profile, or `None`.                 |
| `result`          | Guardrail status, checks, message, and `can_continue`.  |

`stop_if_failed()` accepts the complete wrapper returned by `monitor_data_changes()` and stops only when the resolved result has `can_continue=False`.

## Use in the pipeline notebook

The `03_pc`  pipeline template contains the complete executable workflow for:

* source and target schema validation;
* source and target data-change monitoring;
* fail-fast enforcement;
* profile evidence writing;
* explicit approved-baseline promotion.

Use this page to choose the appropriate presets. Use the notebook template as the implementation reference, and use the generated API reference for exact function parameters and return values.

