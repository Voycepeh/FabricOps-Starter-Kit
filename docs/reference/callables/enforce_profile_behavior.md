# enforce_profile_behavior

Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.

## What this is for and when to use it

Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.

- Use in 02_pipeline to enforce load_behavior expectations against previous accepted catalogue profile evidence.

## When not to use it

- Do not use for simple schema validation or DQ-rule enforcement; use validate_schema or enforce_dq_rules for those checks.

## Example

```python
stability_result = enforce_profile_behavior(spark, df, "METADATA_DATA_CATALOGUE", dataset_name, table_name, stage="target", run_id=run_id, load_behavior="overwrite")
stop_if_failed(stability_result)
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
      <td data-label="Meaning">Spark session used to read ``METADATA_DATA_CATALOGUE`` when ``catalogue_df`` is not supplied.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataframe</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark DataFrame being checked.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Catalogue metadata table that stores profile evidence rows.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Governed dataset identifier used for previous-profile lookup.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Governed source or target table name used for previous-profile lookup.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>stage</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pipeline stage used to keep source and target profiles independent.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Current pipeline run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>load_behavior</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Expected load behavior. ``append`` protects history, ``overwrite`` accepts rebuilt outputs as the new state, and ``skip`` disables only this guardrail.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>watermark_column</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Business watermark column used by append behavior to compare current and previous minimum and maximum profile evidence.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>exclude_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Business or technical columns to exclude from the current profile.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>exclude_run_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Run identifier to exclude from previous-profile lookup. Defaults to ``run_id``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Metadata route from ``00_env_config`` used to read the catalogue table via ``read_lakehouse_table`` when ``catalogue_df`` is not supplied.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>catalogue_df</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Preloaded ``METADATA_DATA_CATALOGUE`` evidence. When provided, no metadata read is performed.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>current_profile</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Current profile evidence that has already been computed for this table. When supplied, this function reuses it instead of profiling ``dataframe`` again.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and profile behavior checks.

## Errors and side effects

**Errors:** Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.

**Side effects:** Reads baseline profile metadata and computes current profile evidence; it does not write target data.

## Related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/guardrails__catalogue_value/"><code>fabricops_kit.guardrails._catalogue_value</code></a>
- <a href="../internal/guardrails__guardrail_exclude_columns/"><code>fabricops_kit.guardrails._guardrail_exclude_columns</code></a>
- <a href="../internal/guardrails__is_greater_than/"><code>fabricops_kit.guardrails._is_greater_than</code></a>
- <a href="../internal/guardrails__is_less_than/"><code>fabricops_kit.guardrails._is_less_than</code></a>
- <a href="../internal/guardrails__is_missing_table_error/"><code>fabricops_kit.guardrails._is_missing_table_error</code></a>
- <a href="../internal/guardrails__latest_catalogue_behavior_profile_row/"><code>fabricops_kit.guardrails._latest_catalogue_behavior_profile_row</code></a>
- <a href="../internal/guardrails__profile_row_count/"><code>fabricops_kit.guardrails._profile_row_count</code></a>
- <a href="../internal/guardrails__profile_watermark_bounds/"><code>fabricops_kit.guardrails._profile_watermark_bounds</code></a>
- <a href="../internal/guardrails__string_value/"><code>fabricops_kit.guardrails._string_value</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/guardrails.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/guardrails.py#L633-L826">View enforce_profile_behavior on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def enforce_profile_behavior(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    run_id: str,
    load_behavior: str,
    watermark_column: str | None = None,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    exclude_run_id: str | None = None,
    config=None,
    env: str | None = None,
    catalogue_df=None,
    current_profile=None,
) -> dict:
    """Enforce profile behavior guardrails for append, overwrite, or skip loads.

    Parameters
    ----------
    spark : Any
        Spark session used to read ``METADATA_DATA_CATALOGUE`` when
        ``catalogue_df`` is not supplied.
    dataframe : Any
        Spark DataFrame being checked.
    metadata_table : str
        Catalogue metadata table that stores profile evidence rows.
    dataset_name : str
        Governed dataset identifier used for previous-profile lookup.
    table_name : str
        Governed source or target table name used for previous-profile lookup.
    stage : str
        Pipeline stage used to keep source and target profiles independent.
    run_id : str
        Current pipeline run identifier.
    load_behavior : {"append", "overwrite", "skip"}
        Expected load behavior. ``append`` protects history, ``overwrite`` accepts
        rebuilt outputs as the new state, and ``skip`` disables only this
        guardrail.
    watermark_column : str, optional
        Business watermark column used by append behavior to compare current and
        previous minimum and maximum profile evidence.
    exclude_columns : list-like, optional
        Business or technical columns to exclude from the current profile.
    exclude_run_id : str, optional
        Run identifier to exclude from previous-profile lookup. Defaults to
        ``run_id``.
    config, env : object, str, optional
        Metadata route from ``00_env_config`` used to read the catalogue table via
        ``read_lakehouse_table`` when ``catalogue_df`` is not supplied.
    catalogue_df : DataFrame or iterable of mappings, optional
        Preloaded ``METADATA_DATA_CATALOGUE`` evidence. When provided, no
        metadata read is performed.
    current_profile : DataFrame or iterable of mappings, optional
        Current profile evidence that has already been computed for this table.
        When supplied, this function reuses it instead of profiling
        ``dataframe`` again.

    Returns
    -------
    dict
        Standard guardrail result with profile behavior status, continuation
        decision, and catalogue evidence fields for ``write_catalogue_evidence``.

    Notes
    -----
    This guardrail uses existing profile evidence: row count plus the configured
    watermark column's ``min_value`` and ``max_value``. Schema and DQ checks are
    enforced by their own guardrails.
    """
    behavior = str(load_behavior or "").lower().strip()
    if behavior not in {"append", "overwrite", "skip"}:
        raise ValueError("load_behavior must be one of: append, overwrite, skip")

    effective_exclude_columns = _guardrail_exclude_columns(exclude_columns)
    current_profile_df = current_profile
    if current_profile_df is None:
        from fabricops_kit.data_profiling import profile_dataframe

        current_profile_df = profile_dataframe(dataframe, table_name, exclude_columns=effective_exclude_columns)
    current_row_count = _profile_row_count(current_profile_df)
    current_min, current_max = _profile_watermark_bounds(current_profile_df, watermark_column)

    if catalogue_df is None and config is not None and env is not None:
        from fabricops_kit.fabric_input_output import read_lakehouse_table

        try:
            catalogue_df = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
        except Exception as exc:
            if _is_missing_table_error(exc):
                catalogue_df = None
            else:
                raise

    baseline = None
    watermark_baseline = None
    if behavior == "append":
        baseline = _latest_catalogue_behavior_profile_row(
            catalogue_df,
            dataset_name=dataset_name,
            table_name=table_name,
            profile_stage=stage,
            load_behavior=behavior,
            exclude_run_id=exclude_run_id or run_id,
        )
        if watermark_column:
            watermark_baseline = _latest_catalogue_behavior_profile_row(
                catalogue_df,
                dataset_name=dataset_name,
                table_name=table_name,
                profile_stage=stage,
                load_behavior=behavior,
                watermark_column=watermark_column,
                exclude_run_id=exclude_run_id or run_id,
            )

    baseline_run_id = _string_value(_catalogue_value(baseline or {}, "profile_run_id", "run_id"))
    baseline_row_count_raw = _catalogue_value(baseline or {}, "row_count", "profiled_row_count")
    baseline_min = _string_value(_catalogue_value(watermark_baseline or {}, "min_value"))
    baseline_max = _string_value(_catalogue_value(watermark_baseline or {}, "max_value"))
    try:
        baseline_row_count = int(baseline_row_count_raw) if baseline_row_count_raw is not None else None
    except (TypeError, ValueError):
        baseline_row_count = None

    result = {
        "status": "passed",
        "can_continue": True,
        "check_type": "profile_behavior_guardrail",
        "stability_check_enabled": behavior != "skip",
        "load_behavior": behavior,
        "watermark_column": watermark_column or "",
        "row_count": current_row_count,
        "baseline_run_id": baseline_run_id,
        "baseline_row_count": baseline_row_count,
        "baseline_watermark_min_value": baseline_min,
        "baseline_watermark_max_value": baseline_max,
        "stability_status": "passed",
        "stability_can_continue": True,
        "stability_message": "Profile behavior guardrail passed.",
        "stability_difference_summary": "",
    }

    if behavior == "skip":
        message = "Profile behavior guardrail skipped; other guardrails still apply."
        result.update(status="skipped", stability_status="skipped", stability_message=message, message=message)
        return result

    if behavior == "overwrite":
        message = "Overwrite load behavior accepted current profile as the new state."
        result.update(stability_message=message, message=message)
        return result

    if baseline is None:
        message = "No previous accepted append profile was available; current profile establishes the baseline."
        result.update(status="baseline_created", stability_status="baseline_created", stability_message=message, message=message)
        return result

    differences = {}
    if baseline_row_count is not None and current_row_count is not None and current_row_count < baseline_row_count:
        differences["row_count"] = {"previous": baseline_row_count, "current": current_row_count, "rule": "append_row_count_must_not_decrease"}
    if watermark_column:
        if watermark_baseline is None:
            differences["watermark_comparison"] = {
                "status": "skipped",
                "column": watermark_column,
                "reason": "No previous accepted profile row was found for the configured watermark column.",
            }
        else:
            if baseline_min and current_min and _is_greater_than(current_min, baseline_min):
                differences["watermark_min"] = {"previous": baseline_min, "current": current_min, "column": watermark_column, "rule": "append_watermark_min_must_not_move_forward"}
            if baseline_max and current_max and _is_less_than(current_max, baseline_max):
                differences["watermark_max"] = {"previous": baseline_max, "current": current_max, "column": watermark_column, "rule": "append_watermark_max_must_not_move_backwards"}

    blocking_differences = {key: value for key, value in differences.items() if value.get("status") != "skipped"}
    if blocking_differences:
        message = "Append load behavior failed because existing history appears to have been removed or moved."
        result.update(
            status="failed",
            can_continue=False,
            stability_status="failed",
            stability_can_continue=False,
            stability_message=message,
            stability_difference_summary=json.dumps(differences, default=str, sort_keys=True),
            message=message,
        )
        return result

    if differences:
        result["stability_difference_summary"] = json.dumps(differences, default=str, sort_keys=True)
    result["message"] = result["stability_message"]
    return result
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.enforce_profile_behavior`
- Short name: `enforce_profile_behavior`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `633`
- Inbound references count: 1
- Outbound references count: 11

### AI implementation contract

- **required_context:** Requires profile metadata routed through the configured 00_env_config metadata target and a valid source/target stage.
- **inputs:** spark, dataframe, metadata_table, dataset_name, table_name, required stage, run_id, load_behavior, optional watermark column, exclude_columns, and exclude_run_id.
- **output:** Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and profile behavior checks.
- **side_effects:** Reads baseline profile metadata and computes current profile evidence; it does not write target data.
- **failure_modes:** Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.
- **verification:** Verify baseline selection, status, and can_continue before allowing downstream writes or calling stop_if_failed.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/guardrails__catalogue_value/"><code>fabricops_kit.guardrails._catalogue_value</code></a>
- <a href="../internal/guardrails__guardrail_exclude_columns/"><code>fabricops_kit.guardrails._guardrail_exclude_columns</code></a>
- <a href="../internal/guardrails__is_greater_than/"><code>fabricops_kit.guardrails._is_greater_than</code></a>
- <a href="../internal/guardrails__is_less_than/"><code>fabricops_kit.guardrails._is_less_than</code></a>
- <a href="../internal/guardrails__is_missing_table_error/"><code>fabricops_kit.guardrails._is_missing_table_error</code></a>
- <a href="../internal/guardrails__latest_catalogue_behavior_profile_row/"><code>fabricops_kit.guardrails._latest_catalogue_behavior_profile_row</code></a>
- <a href="../internal/guardrails__profile_row_count/"><code>fabricops_kit.guardrails._profile_row_count</code></a>
- <a href="../internal/guardrails__profile_watermark_bounds/"><code>fabricops_kit.guardrails._profile_watermark_bounds</code></a>
- <a href="../internal/guardrails__string_value/"><code>fabricops_kit.guardrails._string_value</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/guardrails.py#L633-L826">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/guardrails.py#L633-L826</a>
- Start line: `633`
- End line: `826`
- Signature:

```python
def enforce_profile_behavior(spark, dataframe, metadata_table: str, dataset_name: str, table_name: str, *, stage: str, run_id: str, load_behavior: str, watermark_column: str | None=None, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, exclude_run_id: str | None=None, config=None, env: str | None=None, catalogue_df=None, current_profile=None) -> dict
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/guardrails__catalogue_value/"><code>fabricops_kit.guardrails._catalogue_value</code></a>
- <a href="../internal/guardrails__guardrail_exclude_columns/"><code>fabricops_kit.guardrails._guardrail_exclude_columns</code></a>
- <a href="../internal/guardrails__is_greater_than/"><code>fabricops_kit.guardrails._is_greater_than</code></a>
- <a href="../internal/guardrails__is_less_than/"><code>fabricops_kit.guardrails._is_less_than</code></a>
- <a href="../internal/guardrails__is_missing_table_error/"><code>fabricops_kit.guardrails._is_missing_table_error</code></a>
- <a href="../internal/guardrails__latest_catalogue_behavior_profile_row/"><code>fabricops_kit.guardrails._latest_catalogue_behavior_profile_row</code></a>
- <a href="../internal/guardrails__profile_row_count/"><code>fabricops_kit.guardrails._profile_row_count</code></a>
- <a href="../internal/guardrails__profile_watermark_bounds/"><code>fabricops_kit.guardrails._profile_watermark_bounds</code></a>
- <a href="../internal/guardrails__string_value/"><code>fabricops_kit.guardrails._string_value</code></a>

</details>
