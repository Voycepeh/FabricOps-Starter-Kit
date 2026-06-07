# monitor_data_changes

**Module:** `drift`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Profile data, compare against the approved baseline, and return a drift guardrail result.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def monitor_data_changes(spark, dataframe, metadata_table: str, dataset_name: str, table_name: str, *, stage: str, preset: str='changing_data', exclude_run_id: str | None=None, distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None, policy_overrides: dict | None=None) -> dict
```

## Parameters

spark : Any
    Spark session used to load existing profile metadata.
dataframe : Any
    Spark DataFrame to profile.
metadata_table : str
    Existing metadata table containing profile evidence rows.
dataset_name : str
    Dataset identifier used to select matching baseline profiles.
table_name : str
    Source or target table name used to select matching baseline profiles.
stage : {"source", "target"}
    Pipeline stage being monitored. Source and target baselines are selected
    independently.
preset : {"changing_data", "fixed_data", "monitor_changing_data", "monitor_fixed_data"}, default="changing_data"
    Data-change monitoring intent. ``changing_data`` compares with the
    latest successful profile and may block, ``fixed_data`` compares with
    an approved baseline and may block, ``monitor_changing_data`` compares
    with the latest successful profile without blocking, and
    ``monitor_fixed_data`` compares with an approved baseline without
    blocking. Presets determine baseline and enforcement behavior;
    ``policy_overrides`` adjusts thresholds only.
exclude_run_id : str, optional
    Current run identifier to exclude from baseline lookup.
distribution_columns : list[str] or set[str] or tuple[str, ...], optional
    Optional allow-list of columns for distribution comparisons.
policy_overrides : dict, optional
    Threshold policy overrides merged with the selected preset defaults.
    Overrides may adjust thresholds only; presets retain control of
    baseline selection and blocking behaviour.

## Returns

dict
    Wrapper containing ``profile`` for the current profile, ``baseline`` for
    the selected baseline profile, and ``result`` for the drift decision.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline`; segment: `Drift monitoring`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__baseline_distribution_args/"><code>fabricops_kit.drift._baseline_distribution_args</code></a>
- <a href="../internal/drift__check_profile_drift/"><code>fabricops_kit.drift._check_profile_drift</code></a>
- <a href="../internal/drift__data_change_preset_config/"><code>fabricops_kit.drift._data_change_preset_config</code></a>
- <a href="../internal/drift__load_latest_profile/"><code>fabricops_kit.drift._load_latest_profile</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="../../api/modules/drift/#monitor_data_changes">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.drift.monitor_data_changes`
- Short name: `monitor_data_changes`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Inbound references count: 0
- Outbound references count: 6

## Outbound references
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__baseline_distribution_args/"><code>fabricops_kit.drift._baseline_distribution_args</code></a>
- <a href="../internal/drift__check_profile_drift/"><code>fabricops_kit.drift._check_profile_drift</code></a>
- <a href="../internal/drift__data_change_preset_config/"><code>fabricops_kit.drift._data_change_preset_config</code></a>
- <a href="../internal/drift__load_latest_profile/"><code>fabricops_kit.drift._load_latest_profile</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>
