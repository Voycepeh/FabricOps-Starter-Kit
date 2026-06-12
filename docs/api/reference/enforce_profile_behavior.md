# enforce_profile_behavior

Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.

## Purpose

Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.

## At a glance

**Use when:**

- Use in 02_pipeline to enforce load_behavior expectations against previous accepted catalogue profile evidence.

**Do not use when:**

- Do not use for simple schema validation or DQ-rule enforcement; use validate_schema or enforce_dq_rules for those checks.

**Example:**

```python
stability_result = enforce_profile_behavior(spark, df, "METADATA_DATA_CATALOGUE", dataset_name, table_name, stage="target", run_id=run_id, load_behavior="overwrite")
stop_if_failed(stability_result)
```

**Errors:**

Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.

**Side effects:**

Reads baseline profile metadata and computes current profile evidence; it does not write target data.

## Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Calls

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._guardrail_exclude_columns`
- `fabricops_kit.guardrails._is_greater_than`
- `fabricops_kit.guardrails._is_less_than`
- `fabricops_kit.guardrails._is_missing_table_error`
- `fabricops_kit.guardrails._latest_catalogue_behavior_profile_row`
- `fabricops_kit.guardrails._profile_row_count`
- `fabricops_kit.guardrails._profile_watermark_bounds`
- `fabricops_kit.guardrails._string_value`

## Callable implementation

### Function details

- Module: `guardrails`
- Classification: Callable
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `639`
- Signature:

```python
def enforce_profile_behavior(spark, dataframe, metadata_table: str, dataset_name: str, table_name: str, *, stage: str, run_id: str, load_behavior: str, watermark_column: str | None=None, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None, exclude_run_id: str | None=None, config=None, env: str | None=None, catalogue_df=None, current_profile=None) -> dict
```

### Parameters

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

### Returns

Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and profile behavior checks.

### Notes

This guardrail uses existing profile evidence: row count plus the configured
watermark column's ``min_value`` and ``max_value``. Schema and DQ checks are
enforced by their own guardrails.

### Public callable source code

- Source file path: `src/fabricops_kit/guardrails.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L639-L832">View enforce_profile_behavior on GitHub</a>

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

        current_profile_df = profile_dataframe(dataframe, table_name, exclude_columns=effective_exclude_columns, config=config)
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

## Internal implementation summary

??? info "Call flow"

    ```text
    enforce_profile_behavior(...)
    ├── _catalogue_value(...)
    ├── _guardrail_exclude_columns(...)
    ├── _is_greater_than(...)
    │   └── _comparable_value(...)
    ├── _is_less_than(...)
    │   └── _comparable_value(...)
    ├── _is_missing_table_error(...)
    ├── _latest_catalogue_behavior_profile_row(...)
    │   ├── _catalogue_value(...)
    │   ├── _is_missing_table_error(...)
    │   ├── _row_to_dict(...)
    │   └── _string_value(...)
    ├── _profile_row_count(...)
    │   └── _normalize_profile(...)
    │       └── _normalize_profile(...) (recursive)
    ├── _profile_watermark_bounds(...)
    │   ├── _normalize_profile(...)
    │   │   └── _normalize_profile(...) (recursive)
    │   └── _string_value(...)
    ├── _string_value(...)
    ├── profile_dataframe(...)
    │   ├── _audit_timestamp_expr(...)
    │   │   └── _get_audit_timezone(...)
    │   │       └── _validate_audit_timezone(...)
    │   ├── _build_distribution_summaries(...)
    │   │   ├── _build_categorical_distribution(...)
    │   │   ├── _build_numeric_distribution(...)
    │   │   └── _numeric_bin_edges(...)
    │   ├── _get_audit_timezone(...)
    │   │   └── _validate_audit_timezone(...)
    │   ├── _get_profiled_columns(...)
    │   └── _is_min_max_supported_type(...)
    └── read_lakehouse_table(...)
        ├── _current_database_matches(...)
        ├── _get_spark(...)
        ├── _get_store(...)
        ├── _normalize_table_name(...)
        ├── _registered_table_identifier(...)
        │   ├── _normalize_table_name(...)
        │   └── _quote_identifier(...)
        └── _uses_registered_metadata_table(...)
    ```

??? info "Internal helpers used: 12"

    This callable uses 12 internal helpers for metadata loading, rule parsing, and other.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_is_missing_table_error</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_normalize_profile</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_catalogue_value</code>, <code>_comparable_value</code>, <code>_guardrail_exclude_columns</code>, <code>_is_greater_than</code>, <code>_is_less_than</code>, <code>_latest_catalogue_behavior_profile_row</code>, <code>_profile_row_count</code>, <code>_profile_watermark_bounds</code>, <code>_row_to_dict</code>, <code>_string_value</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Metadata loading helpers"

            **`def _is_missing_table_error(exc: Exception) -> bool`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L834-L837)

            ```python
            def _is_missing_table_error(exc: Exception) -> bool:
                text = str(exc).lower()
                patterns = ["not found", "table or view not found", "no such table", "cannot resolve", "missing"]
                return any(pattern in text for pattern in patterns)
            ```

        ??? example "Rule parsing helpers"

            **`def _normalize_profile(profile) -> dict | None`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L201-L269)

            ```python
            def _normalize_profile(profile) -> dict | None:
                def row_value(row, *names):
                    for name in names:
                        if isinstance(row, dict) and name in row:
                            return row.get(name)
                        if hasattr(row, "asDict"):
                            data = row.asDict(recursive=True)
                            if name in data:
                                return data.get(name)
                        if hasattr(row, name):
                            return getattr(row, name)
                    return None

                def distribution_payload(value):
                    if value in (None, ""):
                        return None
                    if isinstance(value, dict):
                        return value
                    try:
                        return json.loads(value)
                    except (TypeError, json.JSONDecodeError):
                        return None

                if profile is None:
                    return None
                if isinstance(profile, dict) and "columns" in profile:
                    return profile
                if hasattr(profile, "collect"):
                    return _normalize_profile(profile.collect())
                if isinstance(profile, (list, tuple)):
                    rows = list(profile)
                    if not rows:
                        return None
                    first = rows[0]
                    row_count = row_value(first, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT")
                    table_name = row_value(first, "table_name", "TABLE_NAME", "PROFILED_TABLE_NAME")
                    dataset_name = row_value(first, "dataset_name", "DATASET_NAME")
                    profile_stage = row_value(first, "profile_stage", "PROFILE_STAGE", "EVIDENCE_ROLE")
                    columns = []
                    for row in rows:
                        distribution_type = row_value(row, "distribution_type", "DISTRIBUTION_TYPE")
                        distribution = distribution_payload(row_value(row, "distribution", "DISTRIBUTION", "distribution_json", "DISTRIBUTION_JSON"))
                        column = {
                            "column_name": row_value(row, "column_name", "COLUMN_NAME"),
                            "data_type": row_value(row, "data_type", "DATA_TYPE"),
                            "row_count": row_value(row, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT"),
                            "null_count": row_value(row, "null_count", "NULL_COUNT"),
                            "null_pct": row_value(row, "null_pct", "NULL_PCT", "null_percent", "NULL_PERCENT"),
                            "distinct_count": row_value(row, "distinct_count", "DISTINCT_COUNT"),
                            "distinct_pct": row_value(row, "distinct_pct", "DISTINCT_PCT", "distinct_percent", "DISTINCT_PERCENT"),
                            "min_value": row_value(row, "min_value", "MIN_VALUE"),
                            "max_value": row_value(row, "max_value", "MAX_VALUE"),
                        }
                        if distribution_type:
                            column["distribution_type"] = distribution_type
                        if distribution is not None:
                            column["distribution"] = distribution
                        columns.append(column)
                    return {
                        "dataset_name": dataset_name,
                        "table_name": table_name,
                        "profile_stage": profile_stage,
                        "row_count": row_count,
                        "columns": columns,
                        "profile_status": row_value(first, "profile_status", "PROFILE_STATUS"),
                        "baseline_status": row_value(first, "baseline_status", "BASELINE_STATUS"),
                        "source_change_signal": distribution_payload(row_value(first, "source_change_signal", "SOURCE_CHANGE_SIGNAL_JSON")),
                    }
                return profile
            ```

        ??? example "Other helpers"

            **`def _catalogue_value(row: dict, *names: str)`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L467-L478)

            ```python
            def _catalogue_value(row: dict, *names: str):
                for name in names:
                    if name in row:
                        return row.get(name)
                    upper = name.upper()
                    if upper in row:
                        return row.get(upper)
                    lower = name.lower()
                    for key, value in row.items():
                        if str(key).lower() == lower:
                            return value
                return None
            ```

            **`def _comparable_value(value)`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L485-L494)

            ```python
            def _comparable_value(value):
                if value in (None, ""):
                    return None
                if hasattr(value, "isoformat"):
                    return value.isoformat()
                text = str(value)
                try:
                    return Decimal(text)
                except Exception:
                    return text
            ```

            **`def _guardrail_exclude_columns(exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None) -> set[str]`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L282-L286)

            ```python
            def _guardrail_exclude_columns(exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None) -> set[str]:
                excluded = set(_DEFAULT_STABILITY_EXCLUDE_COLUMNS)
                if exclude_columns:
                    excluded.update(str(column) for column in exclude_columns)
                return excluded
            ```

            **`def _is_greater_than(left, right) -> bool`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L507-L514)

            ```python
            def _is_greater_than(left, right) -> bool:
                left_value = _comparable_value(left)
                right_value = _comparable_value(right)
                if left_value is None or right_value is None:
                    return False
                if isinstance(left_value, Decimal) and isinstance(right_value, Decimal):
                    return left_value > right_value
                return str(left_value) > str(right_value)
            ```

            **`def _is_less_than(left, right) -> bool`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L497-L504)

            ```python
            def _is_less_than(left, right) -> bool:
                left_value = _comparable_value(left)
                right_value = _comparable_value(right)
                if left_value is None or right_value is None:
                    return False
                if isinstance(left_value, Decimal) and isinstance(right_value, Decimal):
                    return left_value < right_value
                return str(left_value) < str(right_value)
            ```

            **`def _latest_catalogue_behavior_profile_row(catalogue_df, *, dataset_name: str, table_name: str, profile_stage: str, load_behavior: str, watermark_column: str | None=None, exclude_run_id: str | None=None) -> dict | None`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L527-L636)

            ```python
            def _latest_catalogue_behavior_profile_row(
                catalogue_df,
                *,
                dataset_name: str,
                table_name: str,
                profile_stage: str,
                load_behavior: str,
                watermark_column: str | None = None,
                exclude_run_id: str | None = None,
            ) -> dict | None:
                if catalogue_df is None:
                    return None

                try:
                    if hasattr(catalogue_df, "collect") and hasattr(catalogue_df, "columns"):
                        from pyspark.sql import functions as F

                        df = catalogue_df
                        columns_by_lower = {str(column).lower(): column for column in df.columns}

                        def catalogue_col(*names: str) -> str | None:
                            for name in names:
                                if name in df.columns:
                                    return name
                                if name.lower() in columns_by_lower:
                                    return columns_by_lower[name.lower()]
                            return None

                        stage = str(profile_stage).lower()
                        stage_roles = [stage, f"{stage}_profile"]
                        if stage == "target":
                            stage_roles.append("output_profile")

                        dataset_col = catalogue_col("dataset_name")
                        table_col = catalogue_col("table_name", "profiled_table_name")
                        stage_col = catalogue_col("profile_stage", "evidence_role")
                        behavior_col = catalogue_col("load_behavior")
                        stability_status_col = catalogue_col("stability_status")
                        profile_status_col = catalogue_col("profile_status")
                        run_col = catalogue_col("profile_run_id", "run_id")
                        time_col = catalogue_col("profiled_at", "run_timestamp", "created_at")
                        column_col = catalogue_col("column_name")
                        required = [dataset_col, table_col, stage_col, behavior_col, stability_status_col]
                        if watermark_column:
                            required.append(column_col)
                        if any(column is None for column in required):
                            return None

                        filters = [
                            F.col(dataset_col) == dataset_name,
                            F.col(table_col) == table_name,
                            F.lower(F.col(stage_col)).isin(stage_roles),
                            F.lower(F.col(behavior_col)) == str(load_behavior).lower(),
                            F.lower(F.col(stability_status_col)).isin("passed", "baseline_created"),
                        ]
                        if profile_status_col:
                            filters.append(F.lower(F.col(profile_status_col)).isin("success", "successful"))
                        if exclude_run_id and run_col:
                            filters.append(F.col(run_col) != exclude_run_id)
                        if watermark_column and column_col:
                            filters.append(F.lower(F.col(column_col)) == str(watermark_column).lower())

                        for condition in filters:
                            df = df.filter(condition)
                        order_columns = []
                        if time_col:
                            order_columns.append(F.col(time_col).desc())
                        if run_col:
                            order_columns.append(F.col(run_col).desc())
                        if order_columns:
                            df = df.orderBy(*order_columns)
                        rows = df.limit(1).collect()
                        return _row_to_dict(rows[0]) if rows else None

                    rows = catalogue_df
                    if isinstance(catalogue_df, dict):
                        rows = [catalogue_df]
                    candidates = []
                    stage = str(profile_stage).lower()
                    stage_roles = {stage, f"{stage}_profile"}
                    if stage == "target":
                        stage_roles.add("output_profile")
                    for raw_row in rows or []:
                        row = _row_to_dict(raw_row)
                        if str(_catalogue_value(row, "dataset_name")) != dataset_name:
                            continue
                        if str(_catalogue_value(row, "table_name", "profiled_table_name")) != table_name:
                            continue
                        if str(_catalogue_value(row, "profile_stage", "evidence_role")).lower() not in stage_roles:
                            continue
                        if str(_catalogue_value(row, "load_behavior")).lower() != str(load_behavior).lower():
                            continue
                        if str(_catalogue_value(row, "stability_status")).lower() not in {"passed", "baseline_created"}:
                            continue
                        profile_status = _catalogue_value(row, "profile_status")
                        if profile_status and str(profile_status).lower() not in {"success", "successful"}:
                            continue
                        if exclude_run_id and str(_catalogue_value(row, "profile_run_id", "run_id")) == str(exclude_run_id):
                            continue
                        if watermark_column and str(_catalogue_value(row, "column_name")).lower() != str(watermark_column).lower():
                            continue
                        candidates.append(row)
                    if not candidates:
                        return None
                    candidates.sort(key=lambda row: (_string_value(_catalogue_value(row, "profiled_at", "run_timestamp", "created_at")), _string_value(_catalogue_value(row, "profile_run_id", "run_id"))), reverse=True)
                    return candidates[0]
                except Exception as exc:
                    if _is_missing_table_error(exc):
                        return None
                    raise
            ```

            **`def _profile_row_count(profile) -> int | None`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L294-L306)

            ```python
            def _profile_row_count(profile) -> int | None:
                normalized = _normalize_profile(profile) or {}
                value = normalized.get("row_count")
                if value in (None, ""):
                    columns = normalized.get("columns") or []
                    if columns:
                        first_column = columns[0] or {}
                        if isinstance(first_column, dict):
                            value = first_column.get("row_count")
                try:
                    return int(value) if value not in (None, "") else None
                except (TypeError, ValueError):
                    return None
            ```

            **`def _profile_watermark_bounds(profile, watermark_column: str | None) -> tuple[str, str]`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L517-L524)

            ```python
            def _profile_watermark_bounds(profile, watermark_column: str | None) -> tuple[str, str]:
                normalized = _normalize_profile(profile) or {}
                if not watermark_column:
                    return "", ""
                for column in normalized.get("columns", []) or []:
                    if str(column.get("column_name") or "").lower() == str(watermark_column).lower():
                        return _string_value(column.get("min_value")), _string_value(column.get("max_value"))
                return "", ""
            ```

            **`def _row_to_dict(row) -> dict`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L272-L279)

            ```python
            def _row_to_dict(row) -> dict:
                if row is None:
                    return {}
                if isinstance(row, dict):
                    return dict(row)
                if hasattr(row, "asDict"):
                    return row.asDict(recursive=True)
                return {name: getattr(row, name) for name in dir(row) if not name.startswith("_")}
            ```

            **`def _string_value(value) -> str`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L481-L482)

            ```python
            def _string_value(value) -> str:
                return "" if value is None else str(value)
            ```


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
- Source line: `639`
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
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._guardrail_exclude_columns`
- `fabricops_kit.guardrails._is_greater_than`
- `fabricops_kit.guardrails._is_less_than`
- `fabricops_kit.guardrails._is_missing_table_error`
- `fabricops_kit.guardrails._latest_catalogue_behavior_profile_row`
- `fabricops_kit.guardrails._profile_row_count`
- `fabricops_kit.guardrails._profile_watermark_bounds`
- `fabricops_kit.guardrails._string_value`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L639-L832">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L639-L832</a>
- Start line: `639`
- End line: `832`
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

### Internal implementation summary

- Internal helper count: 12
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
