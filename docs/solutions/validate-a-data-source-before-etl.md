# Validate a data source before ETL

Validate approved source expectations cheaply before reading the full business dataset and starting ETL.

```text
GOVERNANCE / SETUP
        │
        ▼
Create and approve Guardrails
METADATA_GUARDRAIL
        │
        │ approved expectations
        ▼
────────────────────────────────────

ENGINEERING / PIPELINE RUN
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
             ETL
             ▼
        Row and column DQ Guardrails
             ▼
        Profile and register
```

!!! important "Keep definition and execution separate"

    **Governance defines the Guardrail. Engineering runs the Guardrail. FabricOps records the result.**

## Why validate before ETL

**Source checks can prevent expensive or unsafe pipeline work.** Schema, freshness, and source-change evidence can often be evaluated without loading every business row. Run those checks first; read and transform the full source only when their continuation decisions allow it.

Data Quality (DQ) checks are different because row- and column-level rules need the actual business data. They belong after the full read, not in the cheap pre-read stage.

| Stage | Role | What happens |
| --- | --- | --- |
| Create Guardrails | Governance | Define and approve schema, freshness, change, and DQ expectations. |
| Observe source | Engineering | `observe_table()` cheaply captures the current source state. |
| Check Guardrails | Engineering | `check_schema()`, `check_freshness()`, and `check_changes()` evaluate approved expectations. |
| Record results | FabricOps | Runtime outcomes go to `METADATA_GUARDRAIL_RESULTS`. |
| Read and ETL | Engineering | Full business data is read only after the pre-read checks allow continuation. |
| Check data quality | Engineering | Row- and column-level DQ is evaluated after the actual data is read. |

## 1. Create the Guardrails

**Governance defines what should be true before the pipeline runs.** Approved schema, freshness, change, and DQ expectations belong in `METADATA_GUARDRAIL`; Engineering should not invent them on each execution.

For example, Governance might approve:

- the expected columns and types;
- the maximum acceptable source lag;
- whether a detected source change should warn or block; and
- the row- and column-level DQ rules to run after the read.

See [Review and define Guardrails](../guided-demo/03-enrich-guardrails.md) for the Governance workflow.

## 2. Observe the source

**`observe_table()` collects evidence; it does not make a judgement.** Use the same logical target, schema, and table identity that the full pipeline read will use.

```python
from fabricops_kit import check_changes, check_freshness, check_schema, observe_table

observation_df = observe_table(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
    partition_column="business_date",
    change_column="modified_at",
)
metadata_table_key = observation_df.select("metadata_table_key").first()[0]
```

The observation stores compact source facts in `METADATA_SOURCE_OBSERVATION`: row counts plus the minimum and maximum change value for each partition. Warehouse aggregation is pushed into Warehouse SQL. Lakehouse observation projects only the partition and change columns before distributed aggregation.

!!! note "Evidence is deliberately limited"

    `observe_table()` does not classify partitions, decide whether the pipeline can continue, or build a physical read predicate. It persists a successful observation even when a later Guardrail check fails.

## 3. Check schema

**Check the physical structure before depending on its columns.** `check_schema()` can inspect table metadata without reading the business rows and compare it with the approved schema Guardrail.

```python
schema_result = check_schema(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
    rules_df=guardrail_rules_df,
    metadata_table_key=metadata_table_key,
)
```

Run schema first because freshness and change checks depend on configured partition and change columns being present with usable types. See the [`check_schema()` reference](../api/reference/check_schema.md) for the full contract.

## 4. Check freshness

**Freshness asks whether the observed source has advanced recently enough.** The check evaluates the observation-wide latest `max_change_value` against the approved freshness Guardrail.

```python
freshness_result = check_freshness(
    observation_df,
    rules_df=guardrail_rules_df,
    metadata_table_key=metadata_table_key,
)
```

A source can have the expected schema and still be stale. See the [`check_freshness()` reference](../api/reference/check_freshness.md) for result fields and direct-check options.

## 5. Check changes

**Change checking compares observations rather than rereading every row.** `check_changes()` loads the previous comparable snapshot and classifies partitions as new, changed, removed, reappeared, or unchanged.

```python
changes_result = check_changes(
    observation_df,
    rules_df=guardrail_rules_df,
    metadata_table_key=metadata_table_key,
)
```

The first comparison establishes a baseline. Later comparisons retain affected partition values as structured evidence. Removed partitions are recorded as `is_present=false` tombstones.

This signal is intentionally compact: it does not use row-level `key_hash` or `non_key_hash` comparisons and does not define a mutable refresh window. The future physical read layer—not source observation—owns the decision about how to retrieve affected business data. See the [`check_changes()` reference](../api/reference/check_changes.md) for the supported comparison paths.

## 6. Decide whether the pipeline should continue

**Use each result's continuation decision before performing the full read.** A blocking failure stops the pipeline. A warning records the exception but permits the workflow to continue according to the approved Guardrail.

```python
pre_read_results = (schema_result, freshness_result, changes_result)
can_continue = all(result["can_continue"] for result in pre_read_results)

if not can_continue:
    raise RuntimeError("Source pre-read Guardrails blocked the pipeline")
```

Do not treat change detection itself as a read or merge policy. Its result is evidence that a later physical read implementation can use when deciding whether to skip, restrict, or perform a full read.

## 7. Read the full source

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

## 8. Run Data Quality Guardrails

**DQ checks evaluate the rows and columns now that the data has been read.** Use [`run_table_guardrails()`](../api/reference/run_table_guardrails.md) in the normal pipeline workflow for approved data-quality expectations. Keep this stage separate from compact source observation: it has the complete DataFrame needed to evaluate actual values.

## 9. Store Guardrail Results

**Guardrail intent and runtime outcomes have different owners.** FabricOps writes check outcomes to `METADATA_GUARDRAIL_RESULTS`; it does not overwrite the approved expectations in `METADATA_GUARDRAIL`.

| Metadata table | Responsibility |
| --- | --- |
| `METADATA_GUARDRAIL` | Approved Guardrail intent: what should be true. |
| `METADATA_SOURCE_OBSERVATION` | Compact evidence captured from the current source. |
| `METADATA_GUARDRAIL_RESULTS` | Runtime outcomes: what happened when FabricOps checked. |

The observation and Data Catalogue use the same authoritative `metadata_table_key`, keeping source evidence linked to the physical table later profiled and registered.

## 10. Profile and register

**Finish the successful pipeline by recording the transformed table's observed profile.** After ETL and DQ checks, call [`profile_and_register_table()`](../api/reference/profile_and_register_table.md) so the Data Catalogue describes the delivered table rather than replacing approved Guardrail intent or runtime results.

## How the pieces fit together

| Function | Owns | Does not own |
| --- | --- | --- |
| [`observe_table()`](../api/reference/observe_table.md) | Cheap source evidence and its persistence. | Guardrail judgement or physical read planning. |
| [`check_schema()`](../api/reference/check_schema.md) | Comparison with approved schema intent. | Full business-row validation. |
| [`check_freshness()`](../api/reference/check_freshness.md) | Judgement of the latest observed change value. | Source-change classification. |
| [`check_changes()`](../api/reference/check_changes.md) | Comparison with prior observations and affected-partition evidence. | Target merge policy or read-predicate construction. |
| [`run_table_guardrails()`](../api/reference/run_table_guardrails.md) | Approved DQ checks after the source is read. | Creating Governance intent. |

## Expected result

The pipeline either stops or warns according to approved pre-read Guardrails, or proceeds to the full read with schema, freshness, and change outcomes recorded. After ETL, it evaluates row- and column-level DQ and profiles the delivered table.

## Next

Run the governed workflow in [`02_pipeline`](../guided-demo/04-run-pipeline-with-guardrails.md), then use the individual function references above for implementation details.
