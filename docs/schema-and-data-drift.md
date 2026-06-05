# Schema and data drift guardrails

FabricOps Starter Kit treats schema drift and data drift as small runtime guardrails in the existing notebook flow. They help a pipeline decide whether it can safely continue, while keeping the implementation public-safe, teachable, and lightweight.

Data drift does **not** automatically mean the data is incorrect. It means the current data differs materially from the previous successful profile and may require investigation.

## What each guardrail validates

| Guardrail | What it validates | Typical examples |
| --- | --- | --- |
| Schema drift | Structural changes that affect whether the pipeline can interpret the dataframe. | Added columns, removed columns, data-type changes, nullability changes, and column ordering where a caller chooses to enforce it. |
| Data drift | Changes in observed data distribution after the standard profile has been generated. | Row-count movement, null-rate movement, distinct-rate movement, numeric distribution shifts, categorical distribution shifts, and newly observed categories. |

The production notebook uses `check_schema()` for simple fail-fast schema validation and `check_profile_drift()` for profile-based data drift validation.

## Lightweight runtime flow in `03_pc`

The `03_pc` production notebook evaluates source and target profiles separately. It does **not** compare source data directly against target data.

```text
Profile source
→ compare with previous source profile
→ enforce source data drift
→ transform and write target
→ profile target
→ compare with previous target profile
→ enforce target data drift
→ continue publication
```

The source profile is compared only with the latest previous successful source profile for the same dataset and table. The target profile is compared only with the latest previous successful target profile for the same dataset and table.

The first successful run has no baseline, returns `no_baseline`, and is allowed to continue.

## Profile metadata reuse

Data drift reuses the existing output from `profile_dataframe()` and the existing `METADATA_DATA_CATALOGUE_COLUMN` profile metadata path used by `03_pc`.

No separate data-drift snapshot table is used. No separate drift-evidence record is written. The notebook run status, concise printed summary, and any thrown exception are sufficient runtime evidence for this starter-kit guardrail.

When data drift is enabled, the standard profile can include lightweight distribution summaries:

- numeric columns: fixed bin edges and bin counts;
- categorical columns: top category counts plus an `other_count` bucket.

Nulls stay separate from category values and are still evaluated by the existing null-percentage drift check.

## Metrics checked

`check_profile_drift()` keeps the existing profile checks and adds lightweight distribution checks when both profiles contain distribution information.

| Metric | Meaning |
| --- | --- |
| Row-count percentage change | How much total row count changed from the baseline profile. |
| Null-percentage-point change | How much a column null percentage changed. |
| Distinct-percentage-point change | How much a column distinct percentage changed. |
| Numeric distribution change using PSI | Population Stability Index over comparable numeric profile bins. |
| Categorical distribution change using total variation distance | Half the sum of absolute category-proportion differences across baseline categories, current categories, and the `other` bucket. |
| Newly observed categories | Current top categories that were not present in the baseline top categories. |

This is intentionally not a large statistical monitoring framework. It is a small production guardrail based on the profile that already exists.

## Example `03_pc` configuration

```python
ENABLE_DATA_DRIFT = True

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

`DATA_DRIFT_COLUMNS = None` lets `profile_dataframe()` choose suitable profiled columns. A short explicit list is useful when teams want to focus the guardrail on important business columns.

Policy overrides are passed to `check_profile_drift(policy=DATA_DRIFT_POLICY)`. Unspecified thresholds fall back to the lightweight defaults, including row-count, null-percentage, distinct-percentage, and missing-column checks.

## Runtime outcomes

`check_profile_drift()` returns the existing guardrail shape:

```python
{
    "status": "passed" | "warning" | "failed" | "no_baseline",
    "can_continue": True | False,
    "checks": [...],
    "message": "...",
}
```

### Passed

```text
Target data drift: passed
```

The current profile is within configured thresholds. The notebook continues.

### Warning

```text
Source data drift: warning
- transaction_amount numeric psi: 0.140
```

Warnings surface material movement but do not block execution. The notebook continues.

### Failed

```text
Target data drift: failed
- order_status categorical distance: 0.310
```

Blocking thresholds were met or exceeded. `assert_no_blocking_profile_drift()` raises before the next publication step continues.

### No baseline

```text
Source data drift: no_baseline
```

No previous successful source or target profile exists for the matching stage. This is expected for the first successful run and does not block execution.

## Enforcement rules

The default lightweight profile drift policy is:

```python
{
    "max_row_count_change_percent": 50,
    "max_null_percent_change_points": 20,
    "max_distinct_percent_change_points": 30,
    "warn_numeric_psi": 0.10,
    "block_numeric_psi": 0.25,
    "warn_categorical_distance": 0.10,
    "block_categorical_distance": 0.25,
    "fail_on_missing_column": True,
}
```

For distribution checks:

- values below the warning threshold pass;
- values between the warning and blocking thresholds warn;
- values at or above the blocking threshold fail;
- failed checks set `can_continue=False`;
- warnings do not block execution.

## Design boundaries

This implementation intentionally avoids:

- a separate data-drift metadata table;
- dedicated data-drift snapshot-writing functions;
- persisting every drift comparison as a drift-evidence record;
- comparing source and target profiles directly to one another;
- advanced model-monitoring infrastructure;
- heavy statistical dependencies such as SciPy.

If a team needs a broader monitoring program later, extend the canonical profile and metadata flow first rather than introducing duplicate profiling systems.

Next read: [AI-Assisted Data Quality Rules System](data-quality-rules-system.md), [Metadata Tables](how-fabricops-works/metadata-tables.md), [Function Reference](reference/index.md).
