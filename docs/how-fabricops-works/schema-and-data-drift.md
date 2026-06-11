# Pipeline Guardrails

Pipeline guardrails are the runtime checks inside `02_pipeline` that decide whether a run can continue, continue with warnings, or stop before writing governed outputs.

Read [How FabricOps Works](index.md) first for the standard `01_agreement` → `02_pipeline` → `03_governance` workflow. This page focuses only on the guardrails owned by `02_pipeline`.

![Schema, freshness, profile behavior, and DQ guardrails showing source, transform, and target validation flow](../assets/fabricops-schema-data-guardrails.png){ .full-width }

## Contract expectation versus runtime enforcement

FabricOps keeps the user-facing model simple:

- **Data contract = expectation.** The contract says what the data should look like and which checks matter.
- **Guardrail = enforcement.** A guardrail turns a contract expectation into a runtime pass, warning, fail, or skipped result.
- **`02_pipeline` = runtime enforcement layer.** The pipeline validates schemas, freshness, profile behavior, and approved DQ rules before publishing outputs.
- **`03_governance` = governance and business definition layer.** Governance review defines and approves business context, classifications, and DQ metadata; it does not replace runtime enforcement.

## What guardrails protect

`02_pipeline` is where source data is read, transformed, checked, and written as governed output. Guardrails protect that path by checking:

1. whether the source or target schema still matches what the pipeline expects;
2. whether the expected latest data arrived on time;
3. whether source or target profile behavior matches the configured `load_behavior`;
4. whether approved active DQ rules pass at the source or target stage.

The boundary is simple: `03_governance` can review and approve metadata, but `02_pipeline` owns the runtime decision to continue, warn, or stop.

## Guardrail flow in `02_pipeline`

| Point in the run        | What happens                                                                         | Why it matters                                                            |
| ----------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| After source read       | Validate source schema, source freshness, source profile behavior, and approved active source DQ rules. | Catch upstream structure, freshness, load-behavior, and quality issues early. |
| During transform        | Apply deterministic business logic.                                                               | Keep the output repeatable.                                                  |
| Before target write     | Validate target schema, target freshness, target profile behavior, and approved active target DQ rules. | Avoid publishing stale, unexpected, or error-severity DQ-failing outputs.     |
| After successful checks | Write outputs and metadata evidence.                                                 | Keep governance review and support grounded in what actually ran.         |

## The four guardrail types

| Guardrail                   | What it checks                                                                        | Typical behavior                                                            |
| --------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Schema guardrails           | Whether the source or target structure still matches expected columns and data types. | Stop, warn, or monitor depending on the schema preset.                      |
| Freshness guardrails        | Whether `max(freshness_column)` is recent enough for the configured lag.              | Block or warn when expected latest data has not arrived on time.            |
| Profile behavior guardrails | Whether the current profile follows the configured `load_behavior`.                   | Protect append history, accept normal overwrites, or skip only this check.  |
| DQ guardrails               | Whether approved active DQ rules pass at the source or target stage.                  | Warning failures can continue; error failures block the next critical step. |

Each guardrail returns a notebook result that can be printed as run evidence and passed to `stop_if_failed(...)` when it should block the run.

## Schema guardrails

Schema guardrails check whether the structure of a source or target table still matches what the pipeline expects.

![Schema Guardrail](../assets/fabricops-schema-guardrail.png)

| Preset              | Use when                                                  | Behavior                                                        |
| ------------------- | --------------------------------------------------------- | --------------------------------------------------------------- |
| `strict`            | Production outputs must match the expected schema.        | Stop when columns or data types do not match.                   |
| `allow_new_columns` | New fields are acceptable, but known fields still matter. | Allow additional columns while still checking expected columns. |
| `monitor_only`      | A team wants visibility before blocking runs.             | Record schema differences without stopping the pipeline.        |

## Freshness guardrails

Freshness guardrails answer: did the expected latest data arrive on time? They are separate from profile behavior guardrails. A table can append correctly and still be stale if the newest business date is too old.

The starter config uses beginner-friendly flat fields:

```python
"freshness_column": "business_date",
"freshness_max_lag_days": 1,
"freshness_severity": "blocking",  # "blocking" or "warning"
```

For each configured table, `02_pipeline` checks:

```text
max(freshness_column) >= today - freshness_max_lag_days
```

If today is `2026-06-11` and `freshness_max_lag_days=1`, the latest data must be at least `2026-06-10`. A Warning-severity failure records `status="warning"` and can continue; an Error-severity failure or blocking failure records `status="failed"` and blocks before the next critical step and stops downstream writes. Freshness applies to `append`, `overwrite`, and `skip`; `load_behavior="skip"` skips only profile behavior enforcement.

## Profile behavior guardrails

Profile behavior guardrails use accepted catalogue profile evidence to enforce the configured `load_behavior`. They do not introduce source-kind-specific edit detection for Lakehouse tables, Lakehouse files, or Warehouse tables.

FabricOps reuses profile evidence already written to `METADATA_DATA_CATALOGUE`, especially:

- `row_count`
- `column_name`
- `min_value`
- `max_value`
- `profile_stage`
- `profile_status`
- `stability_status`

The latest accepted previous profile for the same dataset, table, stage, and `load_behavior` becomes the comparison point for the next run.

![Source Stability Guardrail](../assets/fabricops-source-stability-guardrail.png)

| `load_behavior` | Use when | Behavior |
| ---------------- | -------- | -------- |
| `append` | History should be preserved, such as append-only sources or incrementally loaded history. | Compare the current profile against the latest accepted previous append profile. Fail if `row_count` decreases. Fail if the configured watermark column minimum moves forward. Fail if the configured watermark maximum moves backwards. Schema and DQ remain separate guardrails. |
| `overwrite` | Full refresh or rebuild is normal, such as silver/gold outputs. | Do not fail just because the table/output was rebuilt. When schema, freshness, and DQ checks pass, the current profile becomes the new accepted state. |
| `skip` | A dataset is temporarily exempt from profile behavior enforcement. | Return `status="skipped"` and `can_continue=True` for this guardrail only. Schema and DQ guardrails still run. |

## DQ guardrails

DQ guardrails enforce approved active DQ rules from governance metadata. They are separate from schema, freshness, and profile behavior guardrails:

- schema checks validate structure;
- freshness checks validate recency;
- profile behavior checks validate load behavior;
- DQ checks validate business and quality expectations.

This separation keeps failures easier to explain and makes handover evidence clearer for junior engineers.

## How to choose `load_behavior`

Use `append` when removing or rewriting old rows would be suspicious. Use `overwrite` when rebuilding the whole output is expected. Use `skip` only when this specific profile behavior guardrail should not run yet.

```python
source_config = {
    "key": "source_01",
    "layer": "source",
    "table_name": "CHANGE_ME_source_table",
    "stage": "source",
    "load_behavior": "append",
    "watermark_column": "CHANGE_ME_business_date",
    "freshness_column": "CHANGE_ME_business_date",
    "freshness_max_lag_days": 1,
    "freshness_severity": "blocking",
    "expected_schema": {
        "customer_id": "bigint",
        "business_date": "date",
    },
}

target_config = {
    "key": "target_01",
    "target_layer": "unified",
    "target_name": "CHANGE_ME_target_table",
    "stage": "target",
    "load_behavior": "overwrite",
    "write_mode": "overwrite",
    "watermark_column": "business_date",
    "freshness_column": "business_date",
    "freshness_max_lag_days": 1,
    "freshness_severity": "blocking",
    "expected_schema": {
        "customer_id": "bigint",
        "business_date": "date",
    },
}
```
