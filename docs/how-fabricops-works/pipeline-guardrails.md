# Pipeline Guardrails

Pipeline guardrails are the runtime checks inside `02_pipeline` that decide whether a run can continue, continue with warnings, or stop before writing governed outputs.

Read [How FabricOps Works](index.md) first for the standard `01_agreement` → `02_pipeline` → `03_governance` workflow. This page focuses on how `02_pipeline` enforces data contract expectations through schema, freshness, profile behavior, and DQ checks.

![Schema, freshness, profile behavior, and DQ guardrails showing source, transform, and target validation flow](../assets/fabricops-pipeline-guardrails.png){ .full-width }

## Contract expectation versus runtime enforcement

FabricOps keeps contract definition separate from runtime enforcement:

- **Data contract = expectation.** The contract says what the data should look like and which checks matter.
- **Guardrail = runtime enforcement.** A guardrail turns a contract expectation into a runtime pass, warning, fail, or skipped result.
- **`02_pipeline` = technical enforcement layer.** The pipeline validates schema, freshness, profile behavior, and approved DQ rules before publishing outputs.
- **`03_governance` = governance and business definition layer.** Governance review defines and approves business context, classifications, sensitivity, and DQ metadata; it does not replace runtime enforcement.

## Guardrail flow in `02_pipeline`

`02_pipeline` applies guardrails around the business transformation so problems are caught before governed outputs are written.

| Point in the run        | What happens                                                                                         |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| After source read       | Run source schema, freshness, profile behavior, and DQ checks.                                       |
| Transformation          | Apply user-defined deterministic business logic.                                                     |
| Before target write     | Run target schema, freshness, profile behavior, and DQ checks.                                       |
| After successful checks | Write output, lineage, catalogue evidence, guardrail evidence, and the pipeline run summary.         |

Warning-severity failures can continue and remain visible in the run evidence. Error-severity failures record failure evidence and stop downstream writes; a blocking guardrail blocks before the next critical step.

## Guardrail types

| Guardrail | What it checks |
| --- | --- |
| Schema guardrail | Expected columns and data types. |
| Freshness guardrail | Whether `max(freshness_column)` is recent enough based on `freshness_max_lag_days`. |
| Profile behavior guardrail | Whether the current profile follows `load_behavior`: `append`, `overwrite`, or `skip`. |
| DQ guardrail | Approved active DQ rules from governance metadata. |

Each guardrail returns notebook-friendly results that can be displayed as run evidence and used to decide whether the pipeline should continue.

## Schema guardrails

Schema guardrails check whether the source or target structure still matches the expected columns and data types.

![Schema Guardrail](../assets/fabricops-schema-guardrail.png)

| Preset | Use when | Behavior |
| --- | --- | --- |
| `strict` | Production outputs must match the expected schema. | Stop when columns or data types do not match. |
| `allow_new_columns` | New fields are acceptable, but known fields still matter. | Allow additional columns while still checking expected columns. |
| `monitor_only` | A team wants visibility before blocking runs. | Record schema differences without stopping the pipeline. |

## Freshness guardrails

Freshness guardrails answer: did the expected latest data arrive on time? Freshness is separate from profile behavior. A table can append correctly, overwrite correctly, or skip profile behavior enforcement and still be stale if the newest business date is too old.

Freshness applies to `append`, `overwrite`, and `skip`. `load_behavior="skip"` skips only the profile behavior guardrail; it does not skip freshness, schema, or DQ checks.

The starter config uses beginner-friendly flat fields:

```python
"freshness_column": "business_date",
"freshness_max_lag_days": 1,
"freshness_severity": "blocking"
```

For each configured table, `02_pipeline` checks whether `max(freshness_column)` is recent enough for `freshness_max_lag_days`. Warning-severity failures can continue with evidence. Blocking freshness failures stop before the next critical step.

## Profile behavior guardrails

Profile behavior guardrails check whether the current table profile follows the configured `load_behavior`. FabricOps uses daily profile evidence from `METADATA_DATA_CATALOGUE` so each run can compare against the latest accepted profile for the same table, stage, and behavior.

![Source Stability Guardrail](../assets/fabricops-source-stability-guardrail.png)

| `load_behavior` | Use when | Guardrail behavior |
| --- | --- | --- |
| `append` | History should be preserved. | Compare against the latest accepted append profile. Fail if row count decreases, watermark minimum moves forward, or watermark maximum moves backward. |
| `overwrite` | Full refresh/rebuild is normal. | Do not fail because the profile differs from the previous run. Current profile becomes the accepted state when other guardrails pass. |
| `skip` | Temporary exemption. | Return `skipped`/`can_continue=True` for profile behavior only. Schema, freshness, and DQ still run. |

Source-kind-specific edit detection is intentionally out of scope. The guardrail model stays focused on profile evidence and the explicit `load_behavior` setting.

## DQ guardrails

DQ guardrails enforce approved active DQ rules from governance metadata:

- DQ rules are defined and approved in `03_governance`.
- DQ rules are enforced in `02_pipeline`.
- DQ is separate from schema, freshness, and profile behavior.

This separation keeps failures easier to explain: schema checks validate structure, freshness checks validate recency, profile behavior checks validate load behavior, and DQ checks validate approved business and quality expectations.

## Metadata evidence

`02_pipeline` writes evidence so support, governance review, and handover can rely on what actually ran:

| Metadata table | Evidence written |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Profile evidence and guardrail results. |
| `METADATA_PIPELINE_RUNS` | Run-level status, counts, and summary evidence. |
| `METADATA_DATA_LINEAGE_TABLE` | Source-to-target lineage for the pipeline run. |

Profile and guardrail evidence reused by later runs includes `row_count`, `column_name`, `min_value`, `max_value`, `profile_stage`, `profile_status`, `stability_status`, `freshness_status`, and `dq_status`.

## How to choose settings

Use these settings independently so each guardrail explains one kind of risk:

- Use `append` when old rows or history should remain.
- Use `overwrite` when the table is intentionally rebuilt.
- Use `skip` only when this profile behavior guardrail should be disabled.
- Configure freshness separately with `freshness_column`, `freshness_max_lag_days`, and `freshness_severity`.
- Use `schema_preset` separately for schema strictness.
- Let DQ remain controlled by approved governance rules and `dq_preset`.
