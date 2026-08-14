# Validate a data source before ETL

Onboard a dataset with observed evidence, then use approved source checks before expensive work on subsequent runs.

```text
INITIAL ONBOARDING
        │
        ▼
Engineering reads, profiles, and registers the dataset
        │
        ▼
Governance reviews the evidence
        │
        ▼
Governance creates and activates Guardrails
METADATA_GUARDRAIL
        │
────────────────────────────────────

SUBSEQUENT ENGINEERING RUNS
        │
        ▼
observe_table()
        │
        │ cheap source evidence
        ▼
┌──────────────────────────────┐
│ check_schema()               │
│ check_freshness()            │
│ check_changes()              │
└──────────────────────────────┘
        │
        ▼
METADATA_GUARDRAIL_RESULTS
        │
        ▼
Continue?
        │
        ├── No → stop or warn according to the Guardrail
        │
        └── Yes
             ▼
        Full source read
             ▼
        Profile and transform
             ▼
        DataFrame Guardrails
        run_table_guardrails()
             ▼
        Target checks
             ▼
        Write when allowed
```

!!! important "Keep definition and execution separate"

    **Governance defines the Guardrail. Engineering runs the Guardrail. FabricOps records the result.**

## Why validate before ETL

**Source checks can prevent expensive or unsafe pipeline work.** Schema, freshness, and source-change evidence can often be evaluated without loading every business row. Run those checks first; read and transform the full source only when their continuation decisions allow it.

Data Quality (DQ) checks are different because row- and column-level rules need the actual business data. They belong after the full read, not in the cheap pre-read stage.

| Phase | Stage | Role | What happens |
| --- | --- | --- | --- |
| Initial onboarding | Produce evidence | Engineering | Read, profile, and register the dataset in the Data Catalogue. |
| Initial onboarding | Create Guardrails | Governance | Review Engineering evidence, then define and activate schema, freshness, change, profile-behaviour, and DQ expectations. |
| Subsequent runs | Observe source | Engineering | `observe_table()` cheaply captures the current source state. |
| Subsequent runs | Check pre-read Guardrails | Engineering | `check_schema()`, `check_freshness()`, and `check_changes()` evaluate approved source expectations. |
| Subsequent runs | Record results | FabricOps | Runtime outcomes go to `METADATA_GUARDRAIL_RESULTS`. |
| Subsequent runs | Read and transform | Engineering | Full business data is read only after the pre-read checks allow continuation. |
| Subsequent runs | Check DataFrames | Engineering | `run_table_guardrails()` orchestrates applicable source and target DataFrame-level Guardrails before critical steps. |
| Subsequent runs | Write | Engineering | Publish the target only when the applicable continuation decisions allow it. |

## Initial onboarding: produce evidence, then create Guardrails

**Governance needs observed Engineering evidence before it defines expectations for a new dataset.** The initial onboarding run reads, profiles, and registers the dataset. Governance then reviews the `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED` evidence and creates and activates approved Guardrail intent in `METADATA_GUARDRAIL`.

```text
Engineering reads the dataset
        ↓
Profile and register
        ↓
Governance reviews observed evidence
        ↓
Create and activate Guardrails
```

For example, Governance might approve:

- the expected columns and types;
- the maximum acceptable source lag;
- whether a detected source change should warn or block;
- expected profile behaviour; and
- row- and column-level DQ rules.

For source observation, Governance owns both the observation definition and the expected change behaviour. The active source-change Guardrail supplies:

| Guardrail value | Purpose |
| --- | --- |
| `partition_column` | Identifies the source partitions to observe independently. |
| `change_column` | Identifies the value whose observed bounds signal source movement. |
| `change_required` | Requires an observed source change. |
| `no_change_required` | Requires no observed source change. |
| `monitor_only` | Records the observed change status without blocking continuation. |

Exactly one controlled expectation—`change_required`, `no_change_required`, or `monitor_only`—applies to the source-change Guardrail. Engineering does not repeat this policy in pipeline code.

See [Run the initial Development pipeline](../guided-demo/02-run-pipeline.md) and [review and define Guardrails](../guided-demo/03-enrich-guardrails.md) for this onboarding sequence.

!!! note "Established datasets"

    An established governed dataset already has approved Guardrails. Its normal guarded runs therefore begin with the observation and pre-read checks below; Governance does not recreate expectations on every execution.

## Subsequent runs: evaluate approved Guardrails

**Normal guarded runs reuse Governance intent and record new runtime outcomes.** Engineering does not invent expectations during pipeline execution.

| Stage | Role | What happens |
| --- | --- | --- |
| Observe source | Engineering | `observe_table()` cheaply captures the current source state. |
| Check pre-read Guardrails | Engineering | `check_schema()`, `check_freshness()`, and `check_changes()` evaluate approved expectations. |
| Record results | FabricOps | Runtime outcomes go to `METADATA_GUARDRAIL_RESULTS`. |
| Read and ETL | Engineering | Full business data is read only after the pre-read checks allow continuation. |
| Check DataFrames | Engineering | `run_table_guardrails()` evaluates applicable source and target expectations after the data is read. |
| Write | Engineering | The target is written only when the Guardrail results permit publication. |

## 1. Observe the source

**`observe_table()` collects evidence; it does not make a judgement.** Use the same logical target, schema, and table identity that the full pipeline read will use.

```python
from fabricops_kit import check_changes, check_freshness, check_schema, observe_table

observation_df = observe_table(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
)
```

`observe_table()` resolves `partition_column` and `change_column` from the active approved source-change Guardrail. It does not guess them, and Engineering does not redefine Governance-owned policy at runtime. If that Guardrail is missing, inactive, ambiguous, or invalid, observation fails with a clear configuration error instead of collecting evidence under assumed settings.

The observation stores compact source facts in `METADATA_SOURCE_OBSERVATION`: row counts plus the minimum and maximum change value for each partition. Warehouse aggregation is pushed into Warehouse SQL. Lakehouse observation projects only the Governance-defined partition and change columns before distributed aggregation.

!!! note "Evidence is deliberately limited"

    `observe_table()` does not classify partitions, decide whether the pipeline can continue, or build a physical read predicate. It persists a successful observation even when a later Guardrail check fails.

## 2. Check schema

**Check the physical structure before depending on its columns.** `check_schema()` can inspect table metadata without reading the business rows and compare it with the approved schema Guardrail.

```python
schema_result = check_schema(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
)
```

Run schema first because freshness and change checks depend on configured partition and change columns being present with usable types. See the [`check_schema()` reference](../api/reference/check_schema.md) for the full contract.

## 3. Check freshness

**Freshness asks whether the observed source has advanced recently enough.** The check evaluates the observation-wide latest `max_change_value` against the approved freshness Guardrail.

```python
freshness_result = check_freshness(
    observation_df,
)
```

A source can have the expected schema and still be stale. See the [`check_freshness()` reference](../api/reference/check_freshness.md) for result fields and direct-check options.

## 4. Check changes

**Change checking compares observations rather than rereading every row.** `check_changes()` loads the previous comparable snapshot and classifies partitions as new, changed, removed, reappeared, or unchanged.

```python
changes_result = check_changes(
    observation_df,
)
```

The first comparison establishes a baseline. Later comparisons retain affected partition values as structured evidence. Removed partitions are recorded as `is_present=false` tombstones.

This signal remains compact partition evidence. The physical read layer—not source observation—owns predicate construction, and the target pipeline owns its merge behaviour. See the [`check_changes()` reference](../api/reference/check_changes.md) for the supported comparison paths.

## 5. Decide whether the pipeline should continue

**Use each result's continuation decision before performing the full read.** A blocking failure stops the pipeline. A warning records the exception but permits the workflow to continue according to the approved Guardrail.

```python
pre_read_results = (schema_result, freshness_result, changes_result)
can_continue = all(result["can_continue"] for result in pre_read_results)

if not can_continue:
    raise RuntimeError("Source pre-read Guardrails blocked the pipeline")
```

Do not treat change detection itself as a read or merge policy. Its result is evidence that a later physical read implementation can use when deciding whether to skip, restrict, or perform a full read.

## 6. Read the full source

**Read business data only after the cheap checks allow continuation.** At this boundary, Engineering moves from source validation into the normal ETL workload.

```text
Cheap pre-read validation
observe → schema → freshness → changes
                    ↓
              safe to continue
                    ↓
                full read
                    ↓
             transformation
                    ↓
          data-quality checks
```

## 7. Run DataFrame-level Guardrails

**`run_table_guardrails()` orchestrates applicable Guardrails once a DataFrame is available.** The normal pipeline uses it for source and target expectations, including schema, freshness, profile behaviour, and row- or column-level DQ. Keep this DataFrame-level orchestration distinct from the three cheap source checks, which can make their judgements before the full business read.

The [Guided Demo guarded pipeline](../guided-demo/04-run-pipeline-with-guardrails.md) demonstrates this DataFrame-level flow: read and profile the source, evaluate source Guardrails, transform and profile the target, evaluate target Guardrails, and write only when allowed. The pre-read checks on this page are an earlier source-validation gate for pipelines that use the Preview observation interfaces; they complement rather than replace that workflow.

## 8. Store Guardrail Results

**Guardrail intent and runtime outcomes have different owners.** FabricOps writes check outcomes to `METADATA_GUARDRAIL_RESULTS`; it does not overwrite the approved expectations in `METADATA_GUARDRAIL`.

| Metadata table | Responsibility |
| --- | --- |
| `METADATA_DATA_CATALOGUE` / `METADATA_DATA_PROFILED` | Observed schema and profiling evidence reviewed during onboarding. |
| `METADATA_SOURCE_OBSERVATION` | Compact evidence captured from the current source. |
| `METADATA_GUARDRAIL` | Governance-owned observation definition and approved expectations: what should be true. |
| `METADATA_GUARDRAIL_RESULTS` | Runtime outcomes: what happened when FabricOps checked. |

The observation and Data Catalogue use the same authoritative `metadata_table_key`, keeping source evidence linked to the physical table later profiled and registered.

## 9. Profile and register

**Finish the successful pipeline by recording the transformed table's observed profile.** After ETL and DQ checks, call [`profile_and_register_table()`](../api/reference/profile_and_register_table.md) so the Data Catalogue describes the delivered table rather than replacing approved Guardrail intent or runtime results.

## How the pieces fit together

| Function | Owns | Does not own |
| --- | --- | --- |
| [`observe_table()`](../api/reference/observe_table.md) | Cheap source evidence and its persistence. | Guardrail judgement or physical read planning. |
| [`check_schema()`](../api/reference/check_schema.md) | Comparison with approved schema intent. | Full business-row validation. |
| [`check_freshness()`](../api/reference/check_freshness.md) | Judgement of the latest observed change value. | Source-change classification. |
| [`check_changes()`](../api/reference/check_changes.md) | Comparison with prior observations and affected-partition evidence. | Target merge policy or read-predicate construction. |
| [`run_table_guardrails()`](../api/reference/run_table_guardrails.md) | DataFrame-level orchestration of applicable source and target Guardrails. | Creating Governance intent or collecting cheap source observations. |

## Expected result

Initial onboarding produces the evidence Governance needs to approve Guardrails. On subsequent runs, the pipeline either stops or warns according to approved pre-read Guardrails, or proceeds to the full read and DataFrame-level source and target checks before writing the delivered table.

## Next

Run the governed workflow in [`02_pipeline`](../guided-demo/04-run-pipeline-with-guardrails.md), then use the individual function references above for implementation details.
