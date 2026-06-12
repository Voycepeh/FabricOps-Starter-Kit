# enforce_freshness

Enforce whether the latest data arrived within the configured freshness lag.

## When to use this

- Use in 02_pipeline to validate max(freshness_column) is at least today minus freshness_max_lag_days.

## At a glance

**Do not use when:**

- Do not use for schema validation, load-behavior enforcement, or DQ-rule enforcement; use validate_schema, enforce_profile_behavior, or enforce_dq_rules for those checks.

**Errors:**

ValueError when severity is unsupported, lag is missing for a configured column, lag is negative, or reference_date is invalid.

**Side effects:**

Computes max(freshness_column) on the provided DataFrame; it does not write metadata, tables, or files.

## Used in templates

- `02_pipeline`

## Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Calls

- `fabricops_kit.guardrails._coerce_date`
- `fabricops_kit.guardrails._iso_date_value`
- `fabricops_kit.guardrails._max_column_value`

## Function details and source

### Function details

- Module: `guardrails`
- Classification: Callable
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `367`
- Signature:

```python
def enforce_freshness(dataframe, freshness_column: str | None, max_lag_days: int | str | None, severity: str='blocking', *, reference_date: date | datetime | str | None=None) -> dict
```

### Parameters

`dataframe` : `Any`, required
: Spark DataFrame or iterable of row-like mappings to check.

`freshness_column` : `str | None`, required
: Column whose maximum value represents the latest available data date. When omitted, the freshness guardrail is skipped.

`max_lag_days` : `int | str | None`, required
: Maximum allowed lag, in days, between ``reference_date`` and the latest value in ``freshness_column``. Required when ``freshness_column`` is set.

`severity` : `str`, optional
: Whether stale data blocks continuation or returns a non-blocking warning.

`reference_date` : `date | datetime | str | None`, optional
: Date used as "today" for comparison. Defaults to the current local date.

### Returns

Guardrail result dictionary with status, can_continue, latest_value, required_min_value, and freshness evidence fields.

### Notes

Freshness is separate from profile behavior. ``load_behavior="skip"`` only
skips profile behavior enforcement; freshness still runs when configured.

### Example

```python
freshness_result = enforce_freshness(df, "business_date", 1, severity="blocking")
stop_if_failed(freshness_result)
```

### Public callable source code

- Source file path: `src/fabricops_kit/guardrails.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L367-L464">View enforce_freshness on GitHub</a>

```python
def enforce_freshness(
    dataframe,
    freshness_column: str | None,
    max_lag_days: int | str | None,
    severity: str = "blocking",
    *,
    reference_date: date | datetime | str | None = None,
) -> dict:
    """Enforce that a DataFrame contains recent enough data.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame or iterable of row-like mappings to check.
    freshness_column : str or None
        Column whose maximum value represents the latest available data date.
        When omitted, the freshness guardrail is skipped.
    max_lag_days : int or str or None
        Maximum allowed lag, in days, between ``reference_date`` and the latest
        value in ``freshness_column``. Required when ``freshness_column`` is set.
    severity : {"blocking", "warning"}, default="blocking"
        Whether stale data blocks continuation or returns a non-blocking warning.
    reference_date : date, datetime, str, optional
        Date used as "today" for comparison. Defaults to the current local date.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``check_type``, latest value, required minimum value, and message.

    Notes
    -----
    Freshness is separate from profile behavior. ``load_behavior="skip"`` only
    skips profile behavior enforcement; freshness still runs when configured.
    """
    column = str(freshness_column or "").strip()
    normalized_severity = str(severity or "blocking").lower().strip()
    if normalized_severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")

    base_result = {
        "status": "skipped",
        "can_continue": True,
        "check_type": "freshness",
        "freshness_column": column,
        "freshness_max_lag_days": "" if max_lag_days in (None, "") else max_lag_days,
        "freshness_severity": normalized_severity,
        "latest_value": "",
        "required_min_value": "",
        "freshness_status": "skipped",
        "freshness_can_continue": True,
        "freshness_message": "Freshness check skipped because no freshness column is configured.",
        "message": "Freshness check skipped because no freshness column is configured.",
    }
    if not column:
        return base_result
    if max_lag_days is None or str(max_lag_days).strip() == "":
        raise ValueError("max_lag_days is required when freshness_column is set")
    lag_days = int(max_lag_days)
    if lag_days < 0:
        raise ValueError("max_lag_days must be greater than or equal to zero")
    base_result["freshness_max_lag_days"] = lag_days

    today = _coerce_date(reference_date) if reference_date is not None else date.today()
    if today is None:
        raise ValueError("reference_date must be a date, datetime, or ISO date string")
    required_min = today - timedelta(days=lag_days)
    latest_raw = _max_column_value(dataframe, column)
    latest_date = _coerce_date(latest_raw)
    latest_display = _iso_date_value(latest_raw)
    required_display = required_min.isoformat()
    base_result.update(latest_value=latest_display, required_min_value=required_display)

    if latest_date is not None and latest_date >= required_min:
        message = "Freshness check passed."
        base_result.update(
            status="passed",
            can_continue=True,
            freshness_status="passed",
            freshness_can_continue=True,
            freshness_message=message,
            message=message,
        )
        return base_result

    message = f"Freshness check failed: latest {column} is older than allowed lag."
    status = "failed" if normalized_severity == "blocking" else "warning"
    can_continue = normalized_severity == "warning"
    base_result.update(
        status=status,
        can_continue=can_continue,
        freshness_status=status,
        freshness_can_continue=can_continue,
        freshness_message=message,
        message=message,
    )
    return base_result
```

## Internal implementation summary

??? info "Call flow"

    ```text
    enforce_freshness(...)
    ├── _coerce_date(...)
    ├── _iso_date_value(...)
    │   └── _coerce_date(...)
    └── _max_column_value(...)
    ```

??? info "Internal helpers used: 3"

    This callable uses 3 internal helpers for other.

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
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_coerce_date</code>, <code>_iso_date_value</code>, <code>_max_column_value</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Other helpers"

            **`def _coerce_date(value) -> date | None`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L342-L359)

            ```python
            def _coerce_date(value) -> date | None:
                if value in (None, ""):
                    return None
                if isinstance(value, datetime):
                    return value.date()
                if isinstance(value, date):
                    return value
                text = str(value).strip()
                if not text:
                    return None
                try:
                    return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
                except ValueError:
                    pass
                try:
                    return date.fromisoformat(text[:10])
                except ValueError:
                    return None
            ```

            **`def _iso_date_value(value) -> str`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L362-L364)

            ```python
            def _iso_date_value(value) -> str:
                parsed = _coerce_date(value)
                return parsed.isoformat() if parsed is not None else ("" if value is None else str(value))
            ```

            **`def _max_column_value(dataframe, column_name: str)`**

            Source: [`src/fabricops_kit/guardrails.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L309-L339)

            ```python
            def _max_column_value(dataframe, column_name: str):
                if dataframe is None or not column_name:
                    return None
                if hasattr(dataframe, "agg"):
                    from pyspark.sql import functions as F

                    rows = dataframe.agg(F.max(F.col(column_name)).alias("latest_value")).collect()
                    if not rows:
                        return None
                    row = rows[0]
                    if isinstance(row, dict):
                        return row.get("latest_value")
                    if hasattr(row, "asDict"):
                        return row.asDict().get("latest_value")
                    try:
                        return row["latest_value"]
                    except Exception:
                        return getattr(row, "latest_value", None)
                if isinstance(dataframe, dict):
                    values = [dataframe.get(column_name)]
                else:
                    values = []
                    for row in dataframe or []:
                        if isinstance(row, dict):
                            values.append(row.get(column_name))
                        elif hasattr(row, "asDict"):
                            values.append(row.asDict().get(column_name))
                        else:
                            values.append(getattr(row, column_name, None))
                values = [value for value in values if value not in (None, "")]
                return max(values) if values else None
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.enforce_freshness`
- Short name: `enforce_freshness`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `367`
- Inbound references count: 1
- Outbound references count: 3
- Used in templates: 02_pipeline
- Glossary terms: —

### AI implementation contract

- **required_context:** Use in 02_pipeline after schema validation and before downstream writes so stale data can block or warn independently from profile behavior.
- **inputs:** dataframe, freshness_column, max_lag_days, severity, and optional reference_date for deterministic validation.
- **output:** Guardrail result dictionary with status, can_continue, latest_value, required_min_value, and freshness evidence fields.
- **side_effects:** Computes max(freshness_column) on the provided DataFrame; it does not write metadata, tables, or files.
- **failure_modes:** ValueError when severity is unsupported, lag is missing for a configured column, lag is negative, or reference_date is invalid.
- **verification:** Verify freshness_column and freshness_max_lag_days come from the table config and that blocking severity stops writes when can_continue is false.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.guardrails._coerce_date`
- `fabricops_kit.guardrails._iso_date_value`
- `fabricops_kit.guardrails._max_column_value`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L367-L464">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/guardrails.py#L367-L464</a>
- Start line: `367`
- End line: `464`
- Signature:

```python
def enforce_freshness(dataframe, freshness_column: str | None, max_lag_days: int | str | None, severity: str='blocking', *, reference_date: date | datetime | str | None=None) -> dict
```

### Internal relationship graph

### Public related functions

- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 3
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
