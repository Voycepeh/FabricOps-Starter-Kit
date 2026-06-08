# monitor_data_changes

Profile data, compare against the approved baseline, and return a drift guardrail result.

## What this is for and when to use it

Profile data, compare against the approved baseline, and return a drift guardrail result.

- Use in 02_pipeline to compare current profile evidence with an approved or previous baseline and produce a data-change guardrail result.

## When not to use it

- Do not use for simple schema validation or DQ-rule enforcement; use validate_schema or enforce_dq_rules for those checks.

## Example

```python
drift_result = monitor_data_changes(spark, df, "METADATA_PROFILE", dataset_name, table_name, stage="target")
stop_if_failed(drift_result)
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used to load existing profile metadata.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataframe</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark DataFrame to profile.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Existing metadata table containing profile evidence rows.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Dataset identifier used to select matching baseline profiles.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Source or target table name used to select matching baseline profiles.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>stage</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pipeline stage being monitored. Source and target baselines are selected independently.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>preset</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Data-change monitoring intent. ``changing_data`` compares with the latest successful profile and may block, ``fixed_data`` compares with an approved baseline and may block, ``monitor_changing_data`` compares with the latest successful profile without blocking, and ``monitor_fixed_data`` compares with an approved baseline without blocking. Presets determine baseline and enforcement behavior; ``policy_overrides`` adjusts thresholds only.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>exclude_run_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Current run identifier to exclude from baseline lookup.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>distribution_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Optional allow-list of columns for distribution comparisons.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>policy_overrides</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Threshold policy overrides merged with the selected preset defaults. Overrides may adjust thresholds only; presets retain control of baseline selection and blocking behaviour.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and drift checks.

## Errors and side effects

**Errors:** Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.

**Side effects:** Reads baseline profile metadata and computes current profile evidence; it does not write target data.

## Related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__baseline_distribution_args/"><code>fabricops_kit.drift._baseline_distribution_args</code></a>
- <a href="../internal/drift__check_profile_drift/"><code>fabricops_kit.drift._check_profile_drift</code></a>
- <a href="../internal/drift__data_change_preset_config/"><code>fabricops_kit.drift._data_change_preset_config</code></a>
- <a href="../internal/drift__load_latest_profile/"><code>fabricops_kit.drift._load_latest_profile</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/drift.py#L582-L671">View monitor_data_changes on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def monitor_data_changes(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    preset: str = "changing_data",
    exclude_run_id: str | None = None,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    policy_overrides: dict | None = None,
) -> dict:
    """Profile a dataframe and compare it with the baseline selected by a preset.

    Parameters
    ----------
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

    Returns
    -------
    dict
        Wrapper containing ``profile`` for the current profile, ``baseline`` for
        the selected baseline profile, and ``result`` for the drift decision.

    Notes
    -----
    Users choose intent through presets. FabricOps handles profiling, baseline
    selection, comparison, and enforcement mechanics internally.
    """
    from fabricops_kit.data_profiling import profile_dataframe

    config = _data_change_preset_config(preset, policy_overrides)
    baseline_profile = _load_latest_profile(
        spark,
        metadata_table=metadata_table,
        dataset_name=dataset_name,
        table_name=table_name,
        profile_stage=stage,
        exclude_run_id=exclude_run_id,
        baseline_mode=config["baseline_mode"],
    )
    baseline_distribution_args = _baseline_distribution_args(baseline_profile)
    current_profile_df = profile_dataframe(
        dataframe,
        table_name,
        include_distributions=True,
        distribution_columns=distribution_columns,
        distribution_bin_edges=baseline_distribution_args["numeric_edges"],
        categorical_categories=baseline_distribution_args["categorical_values"],
    )
    current_profile = _normalize_profile(current_profile_df)
    result = _check_profile_drift(current_profile, baseline_profile, policy=config["policy"])
    if config["monitor_only"] and not bool(result.get("can_continue", True)):
        original_status = result.get("status")
        result = {**result, "can_continue": True, "status": "warning", "monitor_only": True, "original_status": original_status}
        result["message"] = (
            "Monitor-only data-change check observed blocking drift without stopping execution. "
            f"{result.get('message', '')}"
        ).strip()
    result = {**result, "preset": config["preset"], "baseline_mode": config["baseline_mode"], "policy": config["policy"]}
    return {"profile": current_profile_df, "profile_payload": current_profile, "baseline": baseline_profile, "result": result}
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.drift.monitor_data_changes`
- Short name: `monitor_data_changes`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source line: `582`
- Inbound references count: 0
- Outbound references count: 6

### AI implementation contract

- **required_context:** Requires profile metadata routed through the configured 00_env_config metadata target and a valid source/target stage.
- **inputs:** spark, dataframe, metadata_table, dataset_name, table_name, required stage, preset, optional exclude_run_id, distribution columns, and policy overrides.
- **output:** Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and drift checks.
- **side_effects:** Reads baseline profile metadata and computes current profile evidence; it does not write target data.
- **failure_modes:** Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.
- **verification:** Verify baseline selection, status, and can_continue before allowing downstream writes or calling stop_if_failed.

### Inbound references

Not documented yet

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__baseline_distribution_args/"><code>fabricops_kit.drift._baseline_distribution_args</code></a>
- <a href="../internal/drift__check_profile_drift/"><code>fabricops_kit.drift._check_profile_drift</code></a>
- <a href="../internal/drift__data_change_preset_config/"><code>fabricops_kit.drift._data_change_preset_config</code></a>
- <a href="../internal/drift__load_latest_profile/"><code>fabricops_kit.drift._load_latest_profile</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/drift.py#L582-L671">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/drift.py#L582-L671</a>
- Start line: `582`
- End line: `671`
- Signature:

```python
def monitor_data_changes(spark, dataframe, metadata_table: str, dataset_name: str, table_name: str, *, stage: str, preset: str='changing_data', exclude_run_id: str | None=None, distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None, policy_overrides: dict | None=None) -> dict
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__baseline_distribution_args/"><code>fabricops_kit.drift._baseline_distribution_args</code></a>
- <a href="../internal/drift__check_profile_drift/"><code>fabricops_kit.drift._check_profile_drift</code></a>
- <a href="../internal/drift__data_change_preset_config/"><code>fabricops_kit.drift._data_change_preset_config</code></a>
- <a href="../internal/drift__load_latest_profile/"><code>fabricops_kit.drift._load_latest_profile</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>

</details>
