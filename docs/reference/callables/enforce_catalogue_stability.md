# enforce_catalogue_stability

Compare deterministic profile hashes against append-only catalogue evidence and return a source stability guardrail result.

## What this is for and when to use it

Compare deterministic profile hashes against append-only catalogue evidence and return a source stability guardrail result.

- Use in 02_pipeline to compare current profile evidence with an approved or previous baseline and produce a data-change guardrail result.

## When not to use it

- Do not use for simple schema validation or DQ-rule enforcement; use validate_schema or enforce_dq_rules for those checks.

## Example

```python
stability_result = enforce_catalogue_stability(spark, df, "METADATA_DATA_CATALOGUE", dataset_name, table_name, stage="target")
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
      <td data-label="Meaning">Spark session used to read ``METADATA_DATA_CATALOGUE`` baselines.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataframe</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark DataFrame being checked.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>metadata_table</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Existing catalogue metadata table that stores profile evidence rows.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Governed dataset identifier used for baseline lookup.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Governed source or target table name used for baseline lookup.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>stage</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pipeline stage used to keep source and target baselines independent.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_id</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Current pipeline run identifier.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>data_behavior</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Whether the dataset is expected to be stable in full or only stable for the previously loaded watermark slice.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>stability_check_type</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Comparison strategy. ``skip`` records a non-blocking skipped result.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>watermark_column</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Comparable watermark column required for ``watermark_slice_hash``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>watermark_value</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Current run watermark. When omitted for changing data, the maximum value in ``watermark_column`` is used.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>exclude_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Business or technical columns to exclude from deterministic profiles.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>exclude_run_id</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Run identifier to exclude from baseline lookup. Defaults to ``run_id``.</td>
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
      <td data-label="Meaning">Preloaded ``METADATA_DATA_CATALOGUE`` DataFrame. When provided, no metadata read is performed.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and stability checks.

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
- <a href="../internal/drift__filter_watermark_slice/"><code>fabricops_kit.drift._filter_watermark_slice</code></a>
- <a href="../internal/drift__is_missing_table_error/"><code>fabricops_kit.drift._is_missing_table_error</code></a>
- <a href="../internal/drift__latest_catalogue_stability_row/"><code>fabricops_kit.drift._latest_catalogue_stability_row</code></a>
- <a href="../internal/drift__max_watermark_value/"><code>fabricops_kit.drift._max_watermark_value</code></a>
- <a href="../internal/drift__profile_hash/"><code>fabricops_kit.drift._profile_hash</code></a>
- <a href="../internal/drift__profile_row_count/"><code>fabricops_kit.drift._profile_row_count</code></a>
- <a href="../internal/drift__schema_hash_from_dataframe/"><code>fabricops_kit.drift._schema_hash_from_dataframe</code></a>
- <a href="../internal/drift__stability_exclude_columns/"><code>fabricops_kit.drift._stability_exclude_columns</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/drift.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3d2707796405a2e3e2f36d7a599be05589995508/src/fabricops_kit/drift.py#L584-L756">View enforce_catalogue_stability on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def enforce_catalogue_stability(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    run_id: str,
    data_behavior: str,
    stability_check_type: str,
    watermark_column: str | None = None,
    watermark_value=None,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    exclude_run_id: str | None = None,
    config=None,
    env: str | None = None,
    catalogue_df=None,
) -> dict:
    """Compare the current DataFrame profile with append-only catalogue evidence.

    Parameters
    ----------
    spark : Any
        Spark session used to read ``METADATA_DATA_CATALOGUE`` baselines.
    dataframe : Any
        Spark DataFrame being checked.
    metadata_table : str
        Existing catalogue metadata table that stores profile evidence rows.
    dataset_name : str
        Governed dataset identifier used for baseline lookup.
    table_name : str
        Governed source or target table name used for baseline lookup.
    stage : {"source", "target"}
        Pipeline stage used to keep source and target baselines independent.
    run_id : str
        Current pipeline run identifier.
    data_behavior : {"fixed", "changing"}
        Whether the dataset is expected to be stable in full or only stable for
        the previously loaded watermark slice.
    stability_check_type : {"full_profile_hash", "watermark_slice_hash", "skip"}
        Comparison strategy. ``skip`` records a non-blocking skipped result.
    watermark_column : str, optional
        Comparable watermark column required for ``watermark_slice_hash``.
    watermark_value : Any, optional
        Current run watermark. When omitted for changing data, the maximum
        value in ``watermark_column`` is used.
    exclude_columns : list-like, optional
        Business or technical columns to exclude from deterministic profiles.
    exclude_run_id : str, optional
        Run identifier to exclude from baseline lookup. Defaults to ``run_id``.
    config, env : object, str, optional
        Metadata route from ``00_env_config`` used to read the catalogue table
        via ``read_lakehouse_table`` when ``catalogue_df`` is not supplied.
    catalogue_df : DataFrame, optional
        Preloaded ``METADATA_DATA_CATALOGUE`` DataFrame. When provided, no
        metadata read is performed.

    Returns
    -------
    dict
        Standard guardrail result compatible with ``stop_if_failed``.

    Notes
    -----
    The function does not create a separate history table. It reads the latest
    previous row from the existing append-only catalogue and returns stability
    metadata for ``write_catalogue_evidence`` to append with today's profile.
    """
    from fabricops_kit.data_profiling import profile_dataframe

    behavior = str(data_behavior or "").lower()
    check_type = str(stability_check_type or "").lower()
    if behavior not in {"fixed", "changing"}:
        raise ValueError("data_behavior must be one of: fixed, changing")
    if check_type not in {"full_profile_hash", "watermark_slice_hash", "skip"}:
        raise ValueError("stability_check_type must be one of: full_profile_hash, watermark_slice_hash, skip")
    if check_type == "watermark_slice_hash" and not watermark_column:
        raise ValueError("watermark_column is required for watermark_slice_hash")

    effective_exclude_columns = _stability_exclude_columns(exclude_columns)
    current_profile_df = profile_dataframe(dataframe, table_name, exclude_columns=effective_exclude_columns)
    current_profile_hash = _profile_hash(current_profile_df)
    current_row_count = _profile_row_count(current_profile_df)
    schema_hash = _schema_hash_from_dataframe(dataframe, exclude_columns=effective_exclude_columns)
    effective_watermark = watermark_value
    if check_type == "watermark_slice_hash" and effective_watermark is None:
        effective_watermark = _max_watermark_value(dataframe, str(watermark_column))

    comparable_profile_hash = current_profile_hash
    profile_scope = "full_table"
    profile_filter_expression = ""
    if check_type == "watermark_slice_hash":
        profile_scope = "watermark_slice"
        profile_filter_expression = f"{watermark_column} <= {effective_watermark}"
        comparable_df = _filter_watermark_slice(dataframe, str(watermark_column), effective_watermark)
        comparable_profile_hash = _profile_hash(profile_dataframe(comparable_df, table_name, exclude_columns=effective_exclude_columns))

    if catalogue_df is None and config is not None and env is not None:
        from fabricops_kit.fabric_input_output import read_lakehouse_table

        try:
            catalogue_df = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
        except Exception as exc:
            if _is_missing_table_error(exc):
                catalogue_df = None
            else:
                raise

    baseline = _latest_catalogue_stability_row(
        catalogue_df,
        dataset_name=dataset_name,
        table_name=table_name,
        profile_stage=stage,
        stability_check_type=check_type,
        data_behavior=behavior,
        profile_scope=profile_scope,
        watermark_column=watermark_column,
        exclude_run_id=exclude_run_id or run_id,
    )
    baseline_run_id = str((baseline or {}).get("profile_run_id") or (baseline or {}).get("PROFILE_RUN_ID") or "")
    baseline_watermark_value = (baseline or {}).get("watermark_value", (baseline or {}).get("WATERMARK_VALUE"))
    baseline_profile_hash = (baseline or {}).get("profile_hash", (baseline or {}).get("PROFILE_HASH"))
    if check_type == "watermark_slice_hash":
        baseline_profile_hash = (baseline or {}).get("comparable_profile_hash", (baseline or {}).get("COMPARABLE_PROFILE_HASH"))
        if baseline_watermark_value is not None:
            profile_filter_expression = f"{watermark_column} <= {baseline_watermark_value}"
            comparable_df = _filter_watermark_slice(dataframe, str(watermark_column), baseline_watermark_value)
            comparable_profile_hash = _profile_hash(profile_dataframe(comparable_df, table_name, exclude_columns=effective_exclude_columns))

    result = {
        "status": "passed",
        "can_continue": True,
        "check_type": "catalogue_profile_stability",
        "stability_check_enabled": check_type != "skip",
        "stability_check_type": check_type,
        "data_behavior": behavior,
        "profile_scope": profile_scope,
        "watermark_column": watermark_column or "",
        "watermark_value": str(effective_watermark) if effective_watermark is not None else "",
        "profile_filter_expression": profile_filter_expression,
        "row_count": current_row_count,
        "schema_hash": schema_hash,
        "profile_hash": current_profile_hash,
        "comparable_profile_hash": comparable_profile_hash,
        "baseline_run_id": baseline_run_id,
        "baseline_profile_hash": str(baseline_profile_hash or ""),
        "baseline_watermark_value": str(baseline_watermark_value) if baseline_watermark_value is not None else "",
        "stability_status": "passed",
        "stability_can_continue": True,
        "stability_message": "Current profile matches the previous catalogue profile.",
        "stability_difference_summary": "",
    }
    if check_type == "skip":
        result.update(status="skipped", stability_status="skipped", stability_message="Catalogue profile stability check skipped.", message="Catalogue profile stability check skipped.")
        return result
    if not baseline or not baseline_profile_hash:
        result.update(status="baseline_created", stability_status="baseline_created", baseline_profile_hash="", stability_message="No previous catalogue stability profile was available; current profile establishes the baseline.", message="No previous catalogue stability profile was available; current profile establishes the baseline.")
        return result
    if comparable_profile_hash != str(baseline_profile_hash):
        message = "Previously loaded data changed compared with the prior catalogue profile." if check_type == "watermark_slice_hash" else "Current full profile differs from the previous catalogue profile."
        result.update(
            status="failed",
            can_continue=False,
            stability_status="failed",
            stability_can_continue=False,
            stability_message=message,
            stability_difference_summary=json.dumps({"current_hash": comparable_profile_hash, "baseline_hash": str(baseline_profile_hash)}, sort_keys=True),
            message=message,
        )
        return result
    result["message"] = result["stability_message"]
    return result
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.drift.enforce_catalogue_stability`
- Short name: `enforce_catalogue_stability`
- Module: `drift`
- Classification: Callable
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source line: `584`
- Inbound references count: 0
- Outbound references count: 10

### AI implementation contract

- **required_context:** Requires profile metadata routed through the configured 00_env_config metadata target and a valid source/target stage.
- **inputs:** spark, dataframe, metadata_table, dataset_name, table_name, required stage, run_id, data_behavior, stability_check_type, optional watermark fields, exclude_columns, and exclude_run_id.
- **output:** Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and stability checks.
- **side_effects:** Reads baseline profile metadata and computes current profile evidence; it does not write target data.
- **failure_modes:** Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.
- **verification:** Verify baseline selection, status, and can_continue before allowing downstream writes or calling stop_if_failed.

### Inbound references

Not documented yet

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__filter_watermark_slice/"><code>fabricops_kit.drift._filter_watermark_slice</code></a>
- <a href="../internal/drift__is_missing_table_error/"><code>fabricops_kit.drift._is_missing_table_error</code></a>
- <a href="../internal/drift__latest_catalogue_stability_row/"><code>fabricops_kit.drift._latest_catalogue_stability_row</code></a>
- <a href="../internal/drift__max_watermark_value/"><code>fabricops_kit.drift._max_watermark_value</code></a>
- <a href="../internal/drift__profile_hash/"><code>fabricops_kit.drift._profile_hash</code></a>
- <a href="../internal/drift__profile_row_count/"><code>fabricops_kit.drift._profile_row_count</code></a>
- <a href="../internal/drift__schema_hash_from_dataframe/"><code>fabricops_kit.drift._schema_hash_from_dataframe</code></a>
- <a href="../internal/drift__stability_exclude_columns/"><code>fabricops_kit.drift._stability_exclude_columns</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/drift.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3d2707796405a2e3e2f36d7a599be05589995508/src/fabricops_kit/drift.py#L584-L756">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3d2707796405a2e3e2f36d7a599be05589995508/src/fabricops_kit/drift.py#L584-L756</a>
- Start line: `584`
- End line: `756`
- Signature:

```python
def enforce_catalogue_stability(spark, dataframe, metadata_table: str, dataset_name: str, table_name: str, *, stage: str, run_id: str, data_behavior: str, stability_check_type: str, watermark_column: str | None=None, watermark_value=None, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, exclude_run_id: str | None=None, config=None, env: str | None=None, catalogue_df=None) -> dict
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.drift.validate_schema</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

### Internal implementation helpers

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../internal/drift__filter_watermark_slice/"><code>fabricops_kit.drift._filter_watermark_slice</code></a>
- <a href="../internal/drift__is_missing_table_error/"><code>fabricops_kit.drift._is_missing_table_error</code></a>
- <a href="../internal/drift__latest_catalogue_stability_row/"><code>fabricops_kit.drift._latest_catalogue_stability_row</code></a>
- <a href="../internal/drift__max_watermark_value/"><code>fabricops_kit.drift._max_watermark_value</code></a>
- <a href="../internal/drift__profile_hash/"><code>fabricops_kit.drift._profile_hash</code></a>
- <a href="../internal/drift__profile_row_count/"><code>fabricops_kit.drift._profile_row_count</code></a>
- <a href="../internal/drift__schema_hash_from_dataframe/"><code>fabricops_kit.drift._schema_hash_from_dataframe</code></a>
- <a href="../internal/drift__stability_exclude_columns/"><code>fabricops_kit.drift._stability_exclude_columns</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

</details>
