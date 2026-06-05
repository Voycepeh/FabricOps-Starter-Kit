# Schema and Data Drift Monitoring

Business data quality rules, schema drift checks, and profile drift checks answer different questions. FabricOps uses them together so expected daily changes can continue while unexpected changes are surfaced for review.

| Control | Question answered | Example |
| --- | --- | --- |
| Business data quality rule | Is the current data valid? | `faculty_code` must be from an approved list. |
| Schema drift | Can the pipeline still interpret the structure safely? | A required column is removed or changes type. |
| Profile or data drift | Has the dataset changed beyond expected behaviour? | A null rate rises from 1% to 25%. |

A dataset can pass its business rules and still show suspicious drift. For example, every faculty code may remain valid while one faculty suddenly increases from 20% to 75% of all records.

## Expected change is not automatically drift

Daily datasets are expected to change. FabricOps therefore does not treat every difference from the previous run as a failure.

> FabricOps monitors whether data changed beyond an expected tolerance, rather than whether data changed at all.

Normal daily movement may include:

- row count increasing by 3%;
- null rate moving from 0.10% to 0.12%;
- category distributions moving slightly.

Potential issues may include:

- row count dropping by 60%;
- null rate rising from 0.10% to 18%;
- a previously stable category disappearing;
- a previously unseen department or faculty code appearing;
- one category becoming unexpectedly dominant.

## Reuse the catalogue profile

FabricOps already uses `profile_dataframe()` to create deterministic profiling evidence such as schema, null counts, distinct counts, minimum and maximum values, and samples. Drift monitoring should reuse that canonical evidence rather than create a second profiling system.

```text
Current dataframe
      ↓
profile_dataframe()
      ↓
Catalogue profile evidence
      ↓
Select historical baseline
      ↓
check_schema_drift()
check_profile_drift()
check_partition_drift()
      ↓
summarize_drift_results()
```

The existing drift functions have separate responsibilities:

- `check_schema_drift()` compares the current dataframe structure with a baseline schema snapshot;
- `check_profile_drift()` compares current profile metrics with a baseline profile and configured thresholds;
- `check_partition_drift()` supports partition-level comparison using keys, partitions, and optional watermark baselines;
- `summarize_drift_results()` combines schema, partition, and profile outcomes into one decision.

Not every monitoring signal described on this page is necessarily present in the current canonical profile. Where additional evidence is needed, extend the canonical profile rather than creating parallel profiling tables or functions.

## Monitoring signals

### Schema signals

Schema monitoring can surface structural changes such as:

- columns being added or removed;
- data types changing;
- nullable behaviour changing;
- other schema differences supported by the current drift implementation.

### Dataset signals

Dataset-level monitoring may include:

- row-count movement;
- column-count movement;
- duplicate-key movement where captured;
- data freshness.

### Column profile signals

Column-level monitoring may include:

- null-rate movement;
- distinct-count movement;
- minimum and maximum changes;
- unexpected range movement.

### Categorical signals

Important categorical fields such as faculty, department, status, or programme may require monitoring for:

- new values;
- previously observed values disappearing;
- value frequency;
- percentage distribution;
- unexpected category concentration.

Category-frequency and distribution monitoring may require extending the canonical profile evidence if the current profile stores samples but not the required frequency metrics.

## Select an appropriate baseline

Comparing only with yesterday is unreliable because yesterday may itself be abnormal. FabricOps should support a baseline appropriate to the dataset and its operating pattern.

Possible approaches include:

- the previous successful run;
- the median of the previous seven successful runs;
- a rolling historical baseline;
- the last approved baseline;
- an equivalent academic period;
- the same weekday where daily seasonality matters.

The median of recent successful runs is a sensible general default because it is less affected by one unusual run. Baseline selection should still remain dataset-specific.

For one-time or irregular datasets, the last steward-approved profile may be more appropriate than a rolling baseline.

## Apply thresholds and severity

Drift monitoring is policy-driven. The following is a conceptual example rather than a guaranteed representation of the current API:

```python
drift_policy = {
    "row_count_change_pct": {
        "warning": 10,
        "critical": 30,
    },
    "null_rate_change_points": {
        "warning": 2,
        "critical": 10,
    },
    "distribution_change_points": {
        "warning": 10,
        "critical": 25,
    },
}
```

| Severity | Behaviour |
| --- | --- |
| Info | Record the evidence. |
| Warning | Continue and surface an alert. |
| Critical | Stop processing or require review. |
| Approved change | Accept the change and establish a new expectation or baseline. |

Legitimate changes should not remain permanent alerts. Planned source changes, organisational restructuring, renamed departments, or new faculties should be reviewed and then reflected in an approved rule, policy, or baseline.

## Keep AI in the design and review loop

AI can help analysts propose:

- important columns to monitor;
- likely categorical fields;
- initial drift thresholds;
- candidate allowed-value rules;
- useful partition columns;
- suitable baseline approaches.

AI suggestions remain proposed evidence until a human reviewer approves or edits them. Production execution stays deterministic: runtime notebooks execute approved rules and policies without asking AI to decide whether the data passes.

## Notebook responsibilities

### `02_ex_*`: profile and approve

The exploration notebook should:

1. profile the source data;
2. review catalogue evidence;
3. use AI to propose business rules and drift policies;
4. review and approve the suggestions;
5. establish or approve the initial baseline.

### `03_pc_*`: execute and record

The pipeline contract notebook should:

1. generate the current canonical profile;
2. load the approved business rules and drift policy;
3. load the selected baseline;
4. run business data quality rules;
5. run schema and profile drift checks;
6. store the evidence;
7. warn, quarantine, block, or continue according to approved severity.

No additional notebook template is required for the first implementation. Monitoring belongs in the existing exploration and pipeline contract flow.

## How the controls work together

| Situation | Business DQ | Schema drift | Profile drift |
| --- | --- | --- | --- |
| Null student identifier | Fail | Pass | May alert |
| Required column removed | Cannot run safely | Fail | May also alert |
| New legitimate faculty introduced | May require rule update | Pass | Alert until approved |
| Faculty share rises from 20% to 75% | Pass | Pass | Alert |
| Daily row count increases by 3% | Pass | Pass | Pass |
| Daily row count drops by 70% | May pass individual row checks | Pass | Critical |

Business data quality rules determine whether current values are valid.

Schema drift determines whether the pipeline can safely interpret the data.

Profile drift determines whether the dataset changed beyond expected behaviour.

Next read: [AI-Assisted Data Quality Rules System](data-quality-rules-system.md), [Metadata Tables](how-fabricops-works/metadata-tables.md), [Function Reference](reference/index.md).
