# Validate a data source before ETL

Validate compact source evidence before paying for a full business-data read, then apply DataFrame-level Guardrails before writing a target.

## Why validation happens before expensive work

**Cheap source checks protect the pipeline before profiling, transformation, and publication begin.** Schema, Freshness, and Changes Guardrails answer different questions, but together they determine whether the governed run may continue to the full source read.

```text
INITIAL ONBOARDING
Engineering reads the dataset
→ profile and register
→ Data Catalogue / Data Profiled evidence
→ Governance selects the table
→ author Schema / Freshness / Changes Guardrails
→ author DQ Guardrails when needed
→ Guardrail intent in METADATA_GUARDRAIL

SUBSEQUENT GOVERNED RUNS
observe_table()
→ check_schema() → check_freshness() → check_changes()
→ continuation decision
→ full source read when allowed
→ profile / transform
→ run_table_guardrails()
→ target checks
→ write when allowed
```

## Initial onboarding

**Engineering produces evidence; Governance authors Guardrails; Engineering later evaluates them; FabricOps records the results.**

1. Engineering reads the dataset and calls `profile_and_register_table()`.
2. FabricOps records observed table and column evidence in `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`.
3. Governance selects the catalogued table and reviews that evidence.
4. Governance authors table-level and, where needed, DQ Guardrails.
5. FabricOps stores the authored intent in `METADATA_GUARDRAIL`.

This onboarding read establishes the evidence needed for authoring. The cheap pre-read checks apply on subsequent governed runs, after the relevant Guardrails exist.

## Author Guardrails in Governance

**Governance uses two separate authoring surfaces.** Authoring writes configuration; it is not a separate approval workflow.

### Table-level Guardrails

[`widget_author_guardrails()`](../api/reference/widget_author_guardrails.md) authors configuration for:

- **Schema** — the expected source structure
- **Freshness** — how recent the observed source must be
- **Changes** — how source observations should be compared and judged

### DQ Guardrails

[`widget_author_dq_rules()`](../api/reference/widget_author_dq_rules.md) authors DQ Guardrails separately. DQ authoring does not belong to the table-level Schema, Freshness, and Changes widget.

## Subsequent governed runs

**A governed run observes and checks the source before reading all business data.**

```python
from fabricops_kit import check_changes, check_freshness, check_schema, observe_table

observation = observe_table(
    table_name="orders",
    target="source",
    schema="dbo",
)
schema_result = check_schema("orders", target="source", schema="dbo")
freshness_result = check_freshness(observation)
changes_result = check_changes(observation)

can_continue = all(
    result["can_continue"]
    for result in (schema_result, freshness_result, changes_result)
)
```

The example uses the current public signatures. Consult the generated references for complete return contracts and failure behaviour rather than duplicating API documentation here.

## Observe the source

**[`observe_table()`](../api/reference/observe_table.md) gathers compact source facts.** It records row counts and earliest and latest configured change values by source partition in `METADATA_SOURCE_OBSERVATION`.

Observation does not:

- author Guardrails or invent source policy
- decide severity or whether the pipeline may continue
- own physical read predicates or target merge behaviour
- perform row-level change tracking

The observation is deliberately lightweight. It provides evidence for the checks, not proof that every source cell is unchanged.

## Check schema

**[`check_schema()`](../api/reference/check_schema.md) checks the physical source structure against the configured Schema Guardrail.** It uses the table identity rather than the observation DataFrame and returns structured differences plus a continuation decision.

Run this first so later checks do not rely on columns whose names or types have drifted.

## Check freshness

**[`check_freshness()`](../api/reference/check_freshness.md) checks whether the observed source is sufficiently recent.** It evaluates the canonical evidence returned by `observe_table()` against the configured Freshness Guardrail and returns freshness evidence plus a continuation decision.

## Check changes

**[`check_changes()`](../api/reference/check_changes.md) compares the current observation with previous comparable observations.** It identifies partition-level changes, records removal tombstones where required, evaluates the configured Changes Guardrail, and returns structured evidence plus a continuation decision.

A first comparable observation establishes a baseline. Later observations can show partitions as new, changed, removed, or reappeared. This is compact partition evidence—not inserted, updated, or deleted row tracking.

## Decide whether the pipeline can continue

**Combine the three explicit continuation results before the full read.** A blocking result stops the pipeline at the governed boundary; an allowed result permits the next step.

!!! important "Detection is not read policy"

    Observation and checks can identify changes and whether continuation is allowed. They do not construct incremental predicates, implement skip/full/restricted reads, merge or overwrite targets, apply SCD2 behaviour, or perform remediation. The pipeline owns those choices.

## Read and transform

**Read the full source only when the pre-read results allow it.** Engineering then profiles the available business data, applies visible transformation logic, and prepares the target DataFrame using the normal `02_pipeline` workflow.

## Run DataFrame-level Guardrails

**`run_table_guardrails()` is the DataFrame-level Guardrail orchestrator once business data is available.** It runs the configured table checks—including schema, freshness, profile-change, and DQ checks—records outcomes where configured, and returns whether the pipeline may continue. It is not DQ-only.

Keep this stage distinct from the cheap pre-read source functions: `observe_table()`, `check_schema()`, `check_freshness()`, and `check_changes()`. The pre-read checks complement the normal guarded pipeline; they do not replace source and target DataFrame checks.

See the [generated function reference](../reference/index.md) for the callable catalogue and current API details.

## Metadata ownership

| Ownership | Metadata table | Responsibility |
| --- | --- | --- |
| Governance intent | `METADATA_GUARDRAIL` | Authored Schema, Freshness, Changes, and DQ Guardrail configuration. |
| Source evidence | `METADATA_SOURCE_OBSERVATION` | Compact observed source facts used by the pre-read checks. |
| Runtime judgement | `METADATA_GUARDRAIL_RESULTS` | Check outcomes and continuation decisions recorded by FabricOps. |
| Profiling evidence | `METADATA_DATA_CATALOGUE` | Observed table and column identity produced by Engineering. |
| Profiling evidence | `METADATA_DATA_PROFILED` | Observed profiles produced by Engineering and reviewed during authoring. |

## How the functions fit together

| Stage | Function | Responsibility |
| --- | --- | --- |
| Onboard | `profile_and_register_table()` | Produce catalogue and profiling evidence from the initial read. |
| Author | `widget_author_guardrails()` | Author table-level Schema, Freshness, and Changes configuration. |
| Author | `widget_author_dq_rules()` | Author DQ Guardrails separately. |
| Pre-read | `observe_table()` | Collect and persist compact source facts. |
| Pre-read | `check_schema()` | Judge physical structure against Schema intent. |
| Pre-read | `check_freshness()` | Judge recency from the current observation. |
| Pre-read | `check_changes()` | Compare observations and judge configured Changes intent. |
| DataFrame | `run_table_guardrails()` | Orchestrate Guardrails after business data is available. |

## Next

Follow the Guided Demo to [author Guardrails in Governance](../guided-demo/03-enrich-guardrails.md), then [run the pipeline with Guardrails](../guided-demo/04-run-pipeline-with-guardrails.md).
