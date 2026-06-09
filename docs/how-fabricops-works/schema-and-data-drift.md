# Pipeline Guardrails

Pipeline guardrails are checks inside `02_pipeline` that help decide whether a run should continue, warn, or stop before writing outputs.

Read [How FabricOps Works](index.md) first for the standard `01_agreement` → `02_pipeline` → `03_governance` path. This page focuses on the guardrails that the pipeline owns.

![Schema, data-change, and DQ guardrails showing source and target validation flow](../assets/fabricops-schema-data-guardrails.png){ .full-width }

## Where guardrails run

Source checks run before transformation. They validate source schema, compare source profiles with previous append-only catalogue evidence, and optionally evaluate approved active DQ rules for source tables.

Target checks run before publication. They validate transformed target schema, compare proposed target profiles with previous append-only catalogue evidence, and evaluate approved active DQ rules for target tables before outputs are written.

The important boundary is that `02_pipeline` owns blocking behavior. `03_governance` can approve DQ metadata, but those expectations become active only when `02_pipeline` loads them through the DQ guardrail helper.

## Guardrail flow

| Point in the run | What happens | Why it matters |
| --- | --- | --- |
| Before transform | Check the source schema and source stability profile. | Catch unexpected input changes early. |
| During transform | Apply deterministic business logic. | Keep the output repeatable. |
| Before write | Check the target schema, target stability profile, and approved active DQ rules. | Avoid publishing unexpected output changes or error-severity DQ failures. |
| After successful checks | Write outputs and metadata evidence. | Keep review and support grounded in what actually ran. |

## Compact starter pattern

Use a simple pattern first, then add stricter checks only when the team needs them:

```python
# 1. Load environment config and source data.
# 2. Validate the source schema.
# 3. Profile source data and compare it with previous catalogue evidence.
# 4. Transform the data.
# 5. Validate and profile the proposed target.
# 6. Enforce source and target stability checks.
# 7. Enforce approved active DQ rules as aggregate guardrails.
# 8. Stop or warn based on configured guardrails.
# 9. Write the full target only after required checks pass.
# 10. Record profile, lineage, and run metadata evidence.
```

## Three pipeline guardrails

`02_pipeline` treats schema checks, source stability checks, and approved DQ rules as one guardrail family. Schema guardrails check structure, source stability guardrails compare deterministic catalogue profile hashes, and DQ guardrails evaluate human-approved expectations from `METADATA_DQ_RULES`. Each guardrail returns a notebook result that can be printed for run evidence and passed to `stop_if_failed(...)` when it should block.

## Source stability behavior

FabricOps does not use the catalogue to perform generic distribution drift monitoring. Instead, each pipeline run appends source and target profile evidence into `METADATA_DATA_CATALOGUE`. Fixed datasets are expected to match the previous profile exactly. Changing datasets are compared only for the slice that had already been loaded in the previous run, using a configured watermark or comparable filter.

This catches silent reloads, late backfills, and unexpected upstream mutations before data is promoted into governed outputs.

Key rules:

- `METADATA_DATA_CATALOGUE` is append only.
- Each run writes a new profile evidence row for every profiled column.
- The latest previous row for the same dataset, table, and stage becomes the baseline.
- No separate profile history table is introduced.
- Older catalogue rows remain readable. If no previous stability fields exist, the run establishes the first non-blocking baseline.

## Source stability check types

| Setting | Use when | Behavior in plain language |
| --- | --- | --- |
| `data_behavior="fixed"` with `stability_check_type="full_profile_hash"` | Reference, mapping, or other fixed datasets should not change between runs. | Compare today's full deterministic profile hash with the previous full profile hash. |
| `data_behavior="changing"` with `stability_check_type="watermark_slice_hash"` | Tables receive new or changed periods over time. | Compare only today's version of the slice that already existed in the previous run, using the previous watermark value. |
| `stability_check_type="skip"` | A dataset is intentionally exempt for an early build or investigation. | Return a non-blocking skipped result and still allow other evidence to be written. |

For fixed data, the expected logic is:

```text
today_full_profile_hash == previous_full_profile_hash
```

For changing data, the expected logic is:

```text
today profile where watermark_column <= previous_watermark
==
previous stored comparable profile for that watermark
```

After the comparison, today's profile and today's comparable hash are appended as the next baseline.

## DQ guardrail behavior

`03_governance` records human-approved DQ expectations in `METADATA_DQ_RULES`. `02_pipeline` reads the active approved rules for the target table and evaluates them with the same simple guardrail contract used by schema and source stability checks:

- `status`: `passed`, `warning`, or `failed`;
- `can_continue`: whether publication can proceed;
- `checks`: aggregate rule-level outcomes;
- `message`: a concise summary.

Severity controls the result:

| Rule outcome | Guardrail result | Pipeline behavior |
| --- | --- | --- |
| No rule failures | `passed`, `can_continue=True` | Continue and write the full target dataset. |
| Warning-severity failure | `warning`, `can_continue=True` | Log the warning result, tag rows with `_dq_check_status` and `_dq_failed_rules`, and write the full target dataset. |
| Error-severity failure | `failed`, `can_continue=False` | `stop_if_failed(...)` blocks before the target write. |
| Mixed warning and error failures | `failed`, `can_continue=False` | Error severity wins and blocks before the target write. |

FabricOps keeps DQ enforcement intentionally simple. It does not write a separate invalid-row metadata dataset, filter invalid rows out of the target, send alerts, or perform partial target writes. For warning-level failures, the written dataset keeps every row and adds row-level technical annotations (`_dq_check_status` plus `_dq_failed_rules`) so consumers can see warning-only row issues without losing data.

## Schema guardrail starter helpers

`02_pipeline` includes an optional helper cell that can inspect a current DataFrame schema before users fill in `expected_schema`. Use `display_schema_profile(df)` to review column name, Spark datatype, nullable flag, and proposed guardrail datatype. Use `print_schema_guardrail_config(df)` to print copy-paste-ready starter Python code.

The generated dictionary is only a starter schema guardrail. Users must review the proposed columns and normalized types before treating them as the approved expectation for `validate_schema(...)`. The helpers support excluding technical columns and either preserving DataFrame order or sorting columns alphabetically. Common Spark types are normalized to guardrail-friendly values such as `string`, `integer`, `long`, `double`, `decimal(p,s)`, `date`, `timestamp`, and `boolean`.

## Schema presets

| Preset | Use when | Behavior in plain language |
| --- | --- | --- |
| `strict` | Production outputs must match the expected schema. | Stop when columns or data types do not match. |
| `allow_new_columns` | New fields are acceptable, but existing fields still matter. | Allow additional columns while still checking known columns. |
| `monitor_only` | A team wants visibility before blocking runs. | Record schema differences without stopping the pipeline. |

## Evidence produced

Guardrail results are written with existing metadata evidence:

- source and target profile rows in `METADATA_DATA_CATALOGUE`, including stability hash fields;
- lineage rows in `METADATA_DATA_LINEAGE_TABLE`;
- runtime summary rows in `METADATA_PIPELINE_RUNS`.

This evidence helps `03_governance`, support teams, and future maintainers understand what the pipeline checked and why it did or did not write outputs.

## What this is not

Pipeline guardrails are not a separate data contract framework and FabricOps does not require separate data contracts. Keep the operating model lightweight: the pipeline notebook owns the checks it runs, and reviewed metadata can inform those checks when intentionally implemented.
