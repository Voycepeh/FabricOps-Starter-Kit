# Schema and data drift guardrails

FabricOps Starter Kit treats schema drift and data drift as small runtime guardrails in the existing `03_pc` notebook flow. They decide whether a pipeline can continue safely while reusing the standard profile evidence and metadata catalogue rows.

Data drift does **not** automatically mean the data is incorrect. It means the current data differs materially from the selected baseline and may require investigation.

## What each control answers

| Control | Question answered | Notes |
| --- | --- | --- |
| Source-change detection | Is there useful new processing work for this scheduled run? | Optional and disabled by default. Evolving sources can skip when the configured source signal is unchanged. Stable sources still monitor even when no change is expected. |
| Schema drift | Can the pipeline still interpret the dataframe structure safely? | Validates structural changes such as added columns, removed columns, data-type changes, nullability changes, and column ordering when a caller chooses to enforce those checks. |
| Profile/data drift | Did observed profile statistics move beyond configured tolerances? | Compares the current standard profile with either the latest successful profile or an approved baseline. |
| Profile evidence storage | What did this run observe? | Stores source and target profile evidence in the existing `METADATA_DATA_CATALOGUE_COLUMN` path. |
| Baseline promotion | Which profile should future runs compare against? | Separate from storage. Latest-successful mode can use later successful evidence; approved mode only uses rows explicitly marked approved. |

No separate data-drift metadata table is used. No separate drift-evidence record is written.

## Source behaviours and baseline modes

`03_pc` supports the two lightweight source behaviours that matter for starter-kit pipelines:

| Source behaviour | Meaning | Recommended baseline mode |
| --- | --- | --- |
| `evolving` | The source is expected to change regularly. Warnings may continue; blocking drift stops publication. | `latest_successful` |
| `stable` | The source is expected to remain unchanged. The scheduled run acts as an integrity monitor and compares to a fixed approved baseline. | `approved` |

The settings are related but explicit so users can override them intentionally:

```python
SOURCE_BEHAVIOUR = "evolving"  # evolving | stable
PROFILE_BASELINE_MODE = "latest_successful"  # latest_successful | approved
```

Unsupported values raise clear notebook errors.

## Lightweight runtime flow

```text
Determine source behaviour
        ↓
Optional source-change check
        ↓
Select latest-successful or approved baseline
        ↓
Profile current source
        ↓
Evaluate schema and profile drift
        ↓
Pass / warn / block
        ↓
Transform and publish only when allowed
        ↓
Store evidence
        ↓
Promote baseline only according to baseline mode
```

Source and target drift remain separate:

```text
Profile source
→ compare with previous source profile
→ enforce source data drift
→ transform and profile target
→ compare with previous target profile
→ enforce target data drift
→ publish target only when allowed
→ store source and target profile evidence
```

The source profile is compared only with a source-stage baseline for the same dataset and profiled table. The target profile is compared only with a target-stage baseline for the same dataset and profiled table. Source profiles are never compared directly with target profiles.

## Baseline selection

`load_latest_profile(..., baseline_mode=...)` reuses the existing profile metadata rows.

### `latest_successful`

This mode selects the latest previous profile that matches dataset, profiled table, source/target stage, and excludes the current execution-level `PROFILE_RUN_ID`. New `03_pc` evidence rows include `PROFILE_STATUS = "successful"`, so latest-successful lookup can filter to successful profile evidence when that field exists.

Every execution gets a unique `RUN_ID`, while `PIPELINE_NAME` stays stable:

```python
PIPELINE_NAME = f"{SOURCE_TABLE}_to_{TARGET_TABLE}"
RUN_ID = f"{PIPELINE_NAME}_{ENV_NAME}_{EXECUTION_TIMESTAMP}"
```

Persisted profile rows use the unique `PROFILE_RUN_ID`, so the current run can be excluded without hiding earlier executions of the same pipeline.

### `approved`

This mode selects rows explicitly marked with:

```text
BASELINE_STATUS = approved
```

When `approved` is requested and no approved baseline exists, the result is `no_baseline`. The notebook does not silently fall back to latest successful evidence.

Current profiles are stored as observed evidence by default. Drifted current profiles do **not** automatically become approved baselines. Approving or replacing a stable-source baseline remains an explicit metadata action outside this lightweight PR; no approval UI is introduced.

## Optional source-change skipping

The source-change check is disabled by default:

```python
ENABLE_SOURCE_CHANGE_CHECK = False
SOURCE_CHANGE_STRATEGY = None
```

Supported lightweight strategies are:

- `watermark`;
- `batch_id`;
- `file_modified_time`;
- `row_count_and_max_timestamp`.

For an `evolving` source, if the configured source signal is unchanged from the selected baseline, the notebook reports:

```text
skipped_no_source_change
```

It then exits successfully without transforming, republishing the target, or writing another full profile.

For a `stable` source, the notebook does **not** skip profiling solely because a source signal is unchanged. Stable-source monitoring is an integrity check: it should still profile and compare against the approved baseline to detect unauthorized or accidental changes.

## Metrics checked

`profile_dataframe()` keeps its existing lightweight output by default. When data drift is enabled, it can add distribution summaries for suitable columns:

- numeric columns: `bin_edges` and `bin_counts`;
- categorical columns: `category_counts`, `other_count`, and newly observed categories when profiling against a baseline vocabulary.

`check_profile_drift()` evaluates:

| Metric | Meaning |
| --- | --- |
| Row-count percentage change | How much total row count changed from the baseline profile. |
| Null-percentage-point change | How much a column null percentage changed. |
| Distinct-percentage-point change | How much a column distinct percentage changed. |
| Numeric distribution change using PSI | Population Stability Index over comparable numeric profile bins. |
| Categorical distribution change using total variation distance | Half the sum of absolute category-proportion differences across baseline categories, current categories, and the `other` bucket. |
| Newly observed categories | Current values that were not in the baseline categorical vocabulary. |

Current numeric distributions reuse baseline bin edges when available. Current categorical distributions can reuse the baseline vocabulary so categories moving into or out of an independently calculated top-N list do not create artificial drift.

## Example configuration

```python
ENABLE_DATA_DRIFT = True
SOURCE_BEHAVIOUR = "evolving"
PROFILE_BASELINE_MODE = "latest_successful"

DATA_DRIFT_COLUMNS = [
    "transaction_amount",
    "customer_segment",
    "order_status",
]

DATA_DRIFT_POLICY = {
    "warn_numeric_psi": 0.10,
    "block_numeric_psi": 0.25,
    "warn_categorical_distance": 0.10,
    "block_categorical_distance": 0.25,
}
```

For stable sources, teams can start with stricter thresholds and then tune intentionally:

```python
SOURCE_BEHAVIOUR = "stable"
PROFILE_BASELINE_MODE = "approved"

STABLE_SOURCE_DRIFT_POLICY = {
    "max_row_count_change_percent": 0,
    "max_null_percent_change_points": 0,
    "max_distinct_percent_change_points": 0,
    "warn_numeric_psi": 0.0,
    "block_numeric_psi": 0.01,
    "warn_categorical_distance": 0.0,
    "block_categorical_distance": 0.01,
    "fail_on_missing_column": True,
}
```

Teams should exclude volatile technical fields from stable-source profiling so the guardrail focuses on fields that are genuinely expected to remain unchanged.

## Runtime outcomes

| Outcome | Continue processing | Publish target |
| --- | ---: | ---: |
| `passed` | yes | yes |
| `warning` | yes | yes |
| `failed` | no | no |
| `no_baseline` | yes | configurable/default yes |
| `skipped_no_source_change` | no further work | no |

Warnings remain visible in notebook output and do not block execution. `assert_no_blocking_profile_drift()` blocks only when `can_continue=False`.

Examples:

```text
Source data drift: no_baseline
Target data drift: passed
Source data drift: warning
- transaction_amount numeric psi: 0.140
Target data drift: failed
- order_status categorical distance: 0.310
skipped_no_source_change
```

## Design boundaries

This implementation intentionally avoids:

- new standalone drift metadata tables;
- streaming-window monitoring;
- CDC orchestration;
- rolling averages or seasonal baselines;
- ML anomaly detection;
- automated baseline learning;
- notification integrations;
- approval user interfaces;
- a second pipeline notebook template;
- heavy statistical libraries.

Next read: [AI-Assisted Data Quality Rules System](data-quality-rules-system.md), [Metadata Tables](how-fabricops-works/metadata-tables.md), [Function Reference](reference/index.md).
