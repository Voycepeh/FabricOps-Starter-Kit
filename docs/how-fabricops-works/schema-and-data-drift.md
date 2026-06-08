# Pipeline Guardrails

Pipeline guardrails are checks inside `02_pipeline` that help decide whether a run should continue, warn, or stop before writing outputs.

Read [How FabricOps Works](index.md) first for the standard `01_agreement` → `02_pipeline` → `03_governance` path. This page focuses on the guardrails that the pipeline owns.

![Schema, data-change, and DQ guardrails showing source and target validation flow](../assets/fabricops-schema-data-guardrails.png){ .full-width }

## Where guardrails run

Source checks run before transformation. They validate source schema, compare source profiles with previous metadata evidence, and optionally evaluate approved active DQ rules for source tables.

Target checks run before publication. They validate transformed target schema, compare proposed target profiles with previous metadata evidence, and evaluate approved active DQ rules for target tables before outputs are written.

The important boundary is that `02_pipeline` owns blocking behavior. `03_governance` can approve DQ metadata, but those expectations become active only when `02_pipeline` loads them through the DQ guardrail helper.

## Guardrail flow

| Point in the run | What happens | Why it matters |
| --- | --- | --- |
| Before transform | Check the source schema and source profile. | Catch unexpected input changes early. |
| During transform | Apply deterministic business logic. | Keep the output repeatable. |
| Before write | Check the target schema, target profile, and approved active DQ rules. | Avoid publishing unexpected output changes or error-severity DQ failures. |
| After successful checks | Write outputs and metadata evidence. | Keep review and support grounded in what actually ran. |

## Compact starter pattern

Use a simple pattern first, then add stricter checks only when the team needs them:

```python
# 1. Load environment config and source data.
# 2. Validate the source schema.
# 3. Profile source data and compare it with previous metadata evidence.
# 4. Transform the data.
# 5. Validate and profile the proposed target.
# 6. Enforce approved active DQ rules as aggregate guardrails.
# 7. Stop or warn based on configured guardrails.
# 8. Write the full target only after required checks pass.
# 9. Record profile, lineage, and run metadata evidence.
```



## DQ guardrail behavior

`03_governance` records human-approved DQ expectations in `METADATA_DQ_RULES`. `02_pipeline` reads the active approved rules for the target table and evaluates them with the same simple guardrail contract used by schema and data-change checks:

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

FabricOps v1 keeps DQ enforcement intentionally simple. It does not write a separate invalid-row metadata dataset, filter invalid rows out of the target, send alerts, or perform partial target writes. For warning-level failures, the written dataset keeps every row and adds row-level technical annotations (`_dq_check_status` plus `_dq_failed_rules`) so consumers can see warning-only row issues without losing data; these annotations support catalogue/profile evidence without changing the guardrail blocking contract. Aggregate DQ summary fields such as `DQ_STATUS`, `DQ_RULE_COUNT`, `DQ_FAILED_RULE_COUNT`, `DQ_WARNING_RULE_COUNT`, `DQ_ERROR_RULE_COUNT`, `DQ_FAILED_ROW_COUNT`, `DQ_FAILED_ROW_PERCENT`, and `DQ_CHECKED_AT` are captured with the existing profiling/catalogue evidence path and can feed dashboards and alerts later without changing the target write path.

## Three pipeline guardrails

`02_pipeline` treats schema checks, data-change monitoring, and approved DQ rules as one guardrail family. Schema guardrails check structure, data-change guardrails compare profile movement, and DQ guardrails evaluate human-approved expectations from `METADATA_DQ_RULES`. Each guardrail returns a notebook result that can be printed for run evidence and passed to `stop_if_failed(...)` when it should block.

## Schema presets

| Preset | Use when | Behavior in plain language |
| --- | --- | --- |
| `strict` | Production outputs must match the expected schema. | Stop when columns or data types do not match. |
| `allow_new_columns` | New fields are acceptable, but existing fields still matter. | Allow additional columns while still checking known columns. |
| `monitor_only` | A team wants visibility before blocking runs. | Record schema differences without stopping the pipeline. |

## Data drift presets

| Preset | Use when | Behavior in plain language |
| --- | --- | --- |
| `changing_data` | Data is expected to change from run to run. | Watch for unusual changes while allowing normal movement. |
| `fixed_data` | Data should stay stable. | Treat unexpected movement as more serious. |
| `monitor_changing_data` | The team wants to learn normal change patterns first. | Record changes without blocking. |
| `monitor_fixed_data` | The team wants visibility on stable data before blocking. | Monitor stable-data expectations without stopping the run. |

Start with monitor settings when the team is still learning the data. Move to blocking settings only when the expected behavior is clear.

## DQ preset

| Preset | Use when | Behavior in plain language |
| --- | --- | --- |
| `approved_rules` | The dataset should enforce DQ expectations approved in `03_governance`. | Read active approved rules from `METADATA_DQ_RULES` and evaluate them as aggregate guardrails. |
| `skip` | A dataset has no approved DQ expectations yet or should not run DQ checks in this notebook. | Return a skipped result and continue without loading DQ rules. |

## How DQ rules are approved

`03_governance` writes approved active rules to `METADATA_DQ_RULES`. `02_pipeline` does not author DQ rules; users only choose `dq_preset` per source or target definition. When the preset is `approved_rules`, `02_pipeline` reads those approved active rules from the configured metadata lakehouse route and enforces them before downstream writes.

## Metadata evidence for review

The thin `02_pipeline` template calls existing FabricOps helpers directly for reads, profiling, schema checks, data-change monitoring, DQ enforcement, blocking, and target writes. Users configure datasets and presets while reusable evidence helpers handle the noisier catalogue, lineage, and runtime metadata plumbing. When guardrails run, `02_pipeline` records useful metadata evidence such as:

- the schema that was checked;
- profile results;
- whether checks passed, warned, or failed;
- aggregate DQ rule outcomes when approved active rules were evaluated;
- warning-only DQ row tags in the target dataset through `_dq_check_status` and `_dq_failed_rules`;
- source and target table context;
- lineage and run context;
- runtime summary rows in `METADATA_PIPELINE_RUNS`.

This evidence helps `03_governance`, support teams, and future maintainers understand what the pipeline checked and why it did or did not write outputs.

## What this is not

Pipeline guardrails are not a separate data contract framework and FabricOps v1.0.0 does not require separate data contracts. Keep the operating model lightweight: the pipeline notebook owns the checks it runs, and reviewed metadata can inform those checks when intentionally implemented.
