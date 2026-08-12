# Validate a data source before ETL

Before transforming or writing data, FabricOps can check whether the source still looks the way the pipeline expects.

| Check | Question it answers | Typical level |
| --- | --- | --- |
| Schema | Is the source structure still what we expect? | Table |
| Freshness | Is the source recent enough? | Table |
| Change | Has previously observed source data changed? | Table |
| Data Quality | Do individual values meet approved rules? | Table or column |

Schema, freshness, and change checks answer different questions. The workflow is designed to let users run them individually while developing and testing a pipeline, or run the approved checks together through [`run_table_guardrails()`](../api/reference/run_table_guardrails.md) in the normal FabricOps workflow.

!!! note "Current and planned interfaces"

    `run_table_guardrails()` is the current public production interface for schema, freshness, profile-change, and Data Quality Guardrails. The standalone `check_schema()`, `check_freshness()`, and `check_source_changes()` examples, row-level change classifications, mutable-window behavior, and `checks=` selection shown below describe the intended development interface; they are not exported public callables yet.

```text
Read source
    ↓
Schema check
    ↓
Freshness check
    ↓
Change check
    ↓
Other Guardrails
    ↓
ETL
```

## Check the schema first

**The schema check protects the assumptions the rest of the pipeline depends on.**

Suppose the pipeline expects:

| Column | Expected type |
| --- | --- |
| `MESSAGE_ID` | `bigint` |
| `STATUS` | `string` |
| `RECEIVED_DATE` | `date` |

The source instead arrives with `RECEIVED_DATE` as a string:

```text
Schema: FAIL

RECEIVED_DATE
Expected: date
Actual: string
```

Freshness and change detection may depend on configured columns such as `RECEIVED_DATE` and `MESSAGE_ID`. FabricOps therefore validates the schema before attempting those checks.

The planned standalone development and debugging check is expressed as:

```python
schema_result = check_schema(
    source_df,
    expected_schema={
        "MESSAGE_ID": "bigint",
        "STATUS": "string",
        "RECEIVED_DATE": "date",
    },
)
```

## Check freshness

**Freshness checks whether the source has advanced as expected.**

```python
freshness_result = check_freshness(
    source_df,
    freshness_column="RECEIVED_DATE",
    max_lag_days=1,
)
```

A current source passes:

```text
Latest RECEIVED_DATE: 2026-08-12
Maximum allowed lag: 1 day
Result: PASS
```

A source whose latest `RECEIVED_DATE` is `2026-08-08` fails the same one-day rule.

A source can have the correct schema but still be stale. FabricOps checks freshness before comparing source changes so old input is not incorrectly treated as the latest state. The integrated Guardrail workflow already provides freshness enforcement through `run_table_guardrails()`.

## Check previously observed data for changes

**The change check asks whether data FabricOps previously observed still looks the same now.**

It can narrow the work in two stages: first identify changed partitions, then inspect the records inside only those partitions.

### Compare partition fingerprints

| Date | Rows | Fingerprint |
| --- | ---: | --- |
| 2026-08-09 | 51,882 | `d42f91...` |
| 2026-08-10 | 52,411 | `71ab22...` |
| 2026-08-11 | 53,004 | `90ce18...` |

FabricOps compares each current fingerprint with the previous observation:

- **Same:** no deeper comparison is needed.
- **Different:** inspect the records inside that partition.

### Compare rows inside a changed partition

The row comparison uses three pieces of evidence:

- `key_hash`: stable identity of the logical record.
- `non_key_hash`: state of the remaining attributes.
- Batch or run context: when FabricOps observed that state.

For example, an earlier observation might contain:

| ID | `key_hash` | `non_key_hash` |
| ---: | --- | --- |
| 10001 | `a81f...` | `111aaa...` |

The same logical record might later contain:

| ID | `key_hash` | `non_key_hash` |
| ---: | --- | --- |
| 10001 | `a81f...` | `92bc44...` |

The unchanged `key_hash` and different `non_key_hash` classify record `10001` as **updated**.

| Comparison | Classification |
| --- | --- |
| New key | Inserted |
| Same key and same state | Unchanged |
| Same key and different state | Updated |
| Previously present key now missing | Deleted |

### Set the mutable window

The configurable refresh window separates expected recent corrections from older source drift:

```python
change_result = check_source_changes(
    current_df,
    previous_df,
    key_columns=["MESSAGE_ID"],
    incremental_column="RECEIVED_DATE",
    refresh_days=7,
)
```

| Configuration | Meaning |
| --- | --- |
| `refresh_days=7` | The latest 7 days are recent and mutable. |
| `refresh_days=30` | The latest 30 days are recent and mutable. |
| `refresh_days=90` | The latest 90 days are recent and mutable. |

With a seven-day window, a three-day-old update is a **recent change**. A 100-day-old update is **historical source drift**.

!!! important "Detection is not action"

    The change check tells FabricOps what changed. It does not decide what to do with the change.

```text
CHANGE DETECTION                 PIPELINE POLICY

Inserted                        Skip
Updated                         Warn
Deleted                 →       Stop
Historical drift                Load difference
Recent change                   Rebuild range
                                SCD2
```

The detector stays neutral so it can be used between files, Bronze, Silver, Gold, or Warehouse sources and targets. The pipeline applies the policy appropriate to its destination:

- A current-state target may replace the affected range.
- An SCD2 target may version changed records.
- A governed production pipeline may stop on unexpected historical drift.

## Run the checks together

**The production path runs the approved source Guardrails as one workflow.**

```python
results = run_table_guardrails(source_tables)
```

The combined result remains easy to scan while retaining details for investigation:

```text
Source Guardrails

Schema      PASS
Freshness   PASS
Change      WARNING

Historical source drift detected: 2026-05-14

Inserted    2
Updated     7
Deleted     6
```

Change belongs beside schema and freshness in the existing Guardrail workflow; it is not a separate subsystem.

## Run only what you are testing

**Planned check selection supports a progressive development workflow.**

Run only schema while developing that expectation:

```python
run_table_guardrails(
    source_tables,
    checks=["schema"],
)
```

```text
Schema      PASS
Freshness   NOT RUN
Change      NOT RUN
```

Then combine schema and freshness:

```python
run_table_guardrails(
    source_tables,
    checks=["schema", "freshness"],
)
```

Finally, omit the selection to run the normal production workflow:

```python
run_table_guardrails(source_tables)
```

This creates a simple learning path: **learn one check → test one check → combine checks → run the normal FabricOps workflow**.

## Keep intent separate from outcomes

All Guardrail execution follows the same metadata story:

| Metadata table | Responsibility |
| --- | --- |
| `METADATA_GUARDRAIL` | What should be true: approved Guardrail intent. |
| `METADATA_GUARDRAIL_RESULTS` | What happened when FabricOps checked: runtime outcomes. |

## Next

Use [`run_table_guardrails()`](../api/reference/run_table_guardrails.md) in [`02_pipeline`](../guided-demo/04-run-pipeline-with-guardrails.md), then review how [Governance enriches and approves Guardrail intent](../guided-demo/03-enrich-guardrails.md).
