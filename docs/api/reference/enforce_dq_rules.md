# enforce_dq_rules

## Signature

```python
def enforce_dq_rules(dataframe, config, env, dataset_name, table_name, *, spark_session=None) -> dict
```

## Summary

Enforce approved active DQ rules as a target-write guardrail without filtering rows.

## Usage note

- Use in pipeline guardrails after governance-approved DQ rules exist for the dataset and table.

**Do not use when:**

- Do not use to filter bad rows, author new DQ rules, or bypass governance review approval.

**Additional context:**

Evaluates approved data-quality rules against a DataFrame and returns guardrail evidence that can block unsafe writes.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `dataframe` | `Any` | Yes | Spark DataFrame to evaluate before the target write. The full DataFrame is never filtered or split by this helper. |
| `config` | `FrameworkConfig or dict` | Yes | Runtime configuration containing the configured metadata lakehouse route from ``00_env_config``. |
| `env` | `str` | Yes | Environment name used to read ``METADATA_DQ_RULES`` from the configured metadata target. |
| `dataset_name` | `str` | Yes | Dataset identifier used with ``table_name`` to scope approved DQ rules when those columns exist in the metadata table. |
| `table_name` | `str` | Yes | Target table name whose approved active DQ rules should be enforced. |
| `spark_session` | `pyspark.sql.SparkSession` | No | Spark session used to read metadata when required by the configured storage helper. |

## Returns

Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.

### Return interpretation

When can_continue is true, active rules passed or only non-blocking issues were found. When false, inspect failing rule details before writing the table.

## Raises / Errors

Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.

### Common failure causes

- No approved active DQ rules exist for the table.
- Rule parameters are invalid or unsupported.
- Required columns are missing from the DataFrame.
- The metadata lakehouse cannot be read.

## Example

```python
dq_result = enforce_dq_rules(df, CONFIG, env, dataset_name, table_name, spark_session=spark)
stop_if_failed(dq_result)
```

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Governance Review](../../how-fabricops-works/governance-review.md)

**Glossary terms**

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## Developer details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1499`
- Signature:

```python
def enforce_dq_rules(dataframe, config, env, dataset_name, table_name, *, spark_session=None) -> dict
```

**Used in templates:**

- `02_pipeline`
- `03_governance`

**Side effects:**

Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.

**Notes:**

This v1 guardrail reads approved active rules from ``METADATA_DQ_RULES`` via
the configured metadata route. It records aggregate rule outcomes only; it
does not quarantine rows, write row-level failure metadata, filter invalid
rows, send alerts, or partially write targets.

## Calls

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._dq_failed_row_count`
- `fabricops_kit.governance_review._dq_summary`
- `fabricops_kit.governance_review._dq_tagged_dataframe`
- `fabricops_kit.governance_review._load_active_dq_rules`
- `fabricops_kit.governance_review._run_dq_guardrail_checks`
- `fabricops_kit.governance_review._summarize_dq_guardrail`

## Internal implementation summary

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in the internal implementation summary.

    ```text
    enforce_dq_rules(...)
    ├── _dq_failed_row_count(...)
    │   ├── _dq_failed_expression(...)
    │   │   └── …
    │   └── _spark_sql_helpers(...)
    ├── _dq_summary(...)
    │   ├── _current_audit_timestamp(...)
    │   │   └── …
    │   └── _summarize_dq_guardrail(...)
    ├── _dq_tagged_dataframe(...)
    │   ├── _dq_failed_expression(...)
    │   │   └── …
    │   └── _spark_sql_helpers(...)
    ├── _load_active_dq_rules(...)
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _coerce_rows(...)
    │   ├── _latest_dq_rule_versions(...)
    │   │   └── …
    │   ├── _spark_sql_helpers(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _run_dq_guardrail_checks(...)
    │   ├── _dq_check_status(...)
    │   ├── _dq_failed_expression(...)
    │   │   └── …
    │   ├── _spark_sql_helpers(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _summarize_dq_guardrail(...)
    └── read_lakehouse_table(...)
        ├── _current_database_matches(...)
        ├── _get_spark(...)
        ├── _get_store(...)
        ├── _normalize_table_name(...)
        ├── _registered_table_identifier(...)
        │   └── …
        └── _uses_registered_metadata_table(...)
    ```

??? info "Internal helpers used: 16"

    This callable uses 16 internal helpers for audit timestamp, metadata loading, validation, rule parsing, rule evaluation, and other.

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
          <td data-label="Area">Audit timestamp</td>
          <td data-label="Helpers"><code>_current_audit_timestamp</code>, <code>_get_audit_timezone</code>, <code>_validate_audit_timezone</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_latest_dq_rule_versions</code>, <code>_load_active_dq_rules</code>, <code>_validate_dq_rules</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Validation</td>
          <td data-label="Helpers"><code>_dq_check_status</code>, <code>_run_dq_guardrail_checks</code></td>
          <td data-label="What they do">Validate inputs and guard conditions before the workflow continues.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_canonical_dq_rule_type</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule evaluation</td>
          <td data-label="Helpers"><code>_dq_failed_expression</code>, <code>_dq_failed_row_count</code>, <code>_dq_summary</code>, <code>_dq_tagged_dataframe</code>, <code>_spark_sql_helpers</code>, <code>_summarize_dq_guardrail</code></td>
          <td data-label="What they do">Convert configured rules into executable checks and evaluation results.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_coerce_rows</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L69-L75)

            ```python
            def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
                """Return the current audit timestamp in the configured audit timezone."""
                tz_name = _get_audit_timezone(config, timezone_name)
                value = datetime.now(ZoneInfo(tz_name))
                if drop_microseconds:
                    value = value.replace(microsecond=0)
                return value.isoformat()
            ```

            **`def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L61-L66)

            ```python
            def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
                """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
                if timezone_name is not None:
                    return _validate_audit_timezone(timezone_name)
                value = getattr(config, "audit_timezone", None) if config is not None else None
                return _validate_audit_timezone(value)
            ```

            **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/config.py#L27-L58)

            ```python
            def _validate_audit_timezone(timezone_name: str | None) -> str:
                """Return a valid IANA audit timezone name.

                Parameters
                ----------
                timezone_name : str or None
                    IANA timezone name to validate. Blank values default to ``"UTC"``.

                Returns
                -------
                str
                    Validated timezone name.

                Raises
                ------
                ValueError
                    If a non-blank value is not a valid IANA timezone name.
                """
                value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
                if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
                    raise ValueError(
                        f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
                        'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
                    )
                try:
                    ZoneInfo(value)
                except ZoneInfoNotFoundError as exc:
                    raise ValueError(
                        f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
                        'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
                    ) from exc
                return value
            ```

        ??? example "Metadata loading helpers"

            **`def _latest_dq_rule_versions(metadata_df, table_name: str, env_name: str | None=None, dataset_name: str | None=None)`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1221-L1242)

            ```python
            def _latest_dq_rule_versions(metadata_df, table_name: str, env_name: str | None = None, dataset_name: str | None = None):
                """Resolve latest append-only DQ metadata rows by stable rule identity."""
                _, F, Window = _spark_sql_helpers()
                columns = set(getattr(metadata_df, "columns", []))
                if "rule_key" in columns:
                    partition_cols = ["rule_key"]
                elif "rule_id" in columns:
                    partition_cols = ["rule_id"]
                else:
                    partition_cols = [name for name in ("metadata_table_key", "column_name", "rule_type") if name in columns]
                order_cols = [name for name in ("_committed_at", "approved_at") if name in columns]
                if not partition_cols:
                    raise ValueError("DQ metadata must include rule_key or rule identity columns.")
                scoped = metadata_df.filter(F.col("table_name") == table_name) if "table_name" in columns else metadata_df
                if env_name is not None and "environment_name" in columns:
                    scoped = scoped.filter(F.col("environment_name") == env_name)
                if dataset_name is not None and "dataset_name" in columns:
                    scoped = scoped.filter(F.col("dataset_name") == dataset_name)
                if not order_cols:
                    return scoped
                w = Window.partitionBy(*[F.col(name) for name in partition_cols]).orderBy(*[F.col(name).desc_nulls_last() for name in order_cols])
                return scoped.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")
            ```

            **`def _load_active_dq_rules(metadata_df, table_name: str, env_name: str | None=None, dataset_name: str | None=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1245-L1280)

            ```python
            def _load_active_dq_rules(metadata_df, table_name: str, env_name: str | None = None, dataset_name: str | None = None) -> list[dict[str, Any]]:
                """Load active approved DQ rules from append-only metadata rows."""
                _, F, _ = _spark_sql_helpers()
                columns = set(getattr(metadata_df, "columns", []))
                latest = _latest_dq_rule_versions(metadata_df, table_name, env_name=env_name, dataset_name=dataset_name)
                if "is_active" in columns:
                    latest = latest.filter(F.col("is_active") == True)
                if "action_type" in columns:
                    latest = latest.filter(F.lower(F.coalesce(F.col("action_type"), F.lit("created"))) != "deactivated")
                if "review_status" in columns:
                    latest = latest.filter(F.lower(F.coalesce(F.col("review_status"), F.lit("approved"))) == "approved")

                rules: list[dict[str, Any]] = []
                for row in _coerce_rows(latest.collect()):
                    params_raw = row.get("rule_parameters_json") or "{}"
                    try:
                        params = json.loads(params_raw) if isinstance(params_raw, str) else dict(params_raw)
                    except Exception:
                        params = {}
                    columns_value = params.get("columns") or row.get("columns") or row.get("column_name")
                    if isinstance(columns_value, str):
                        rule_columns = [c.strip() for c in columns_value.split(",") if c.strip()]
                    else:
                        rule_columns = list(columns_value or [])
                    params = {k: v for k, v in params.items() if k != "columns"}
                    rules.append(
                        {
                            "rule_id": str(row.get("rule_id") or ""),
                            "rule_type": _canonical_dq_rule_type(row.get("rule_type")),
                            "columns": rule_columns,
                            "severity": str(row.get("severity") or "warning"),
                            "description": str(row.get("description") or ""),
                            **params,
                        }
                    )
                return _validate_dq_rules(rules)
            ```

            **`def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1146-L1219)

            ```python
            def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
                """Validate canonical DQ rules before loading or enforcement."""
                if not isinstance(rules, list):
                    raise ValueError("DQ rules must be a list of dictionaries.")

                optional_common = {"severity", "description", "rule_id", "is_active", "review_status"}
                del optional_common  # Documents intentionally accepted fields for callers and tests.

                def require_columns(rule: dict[str, Any], count: int | None = None, *, minimum: int | None = None) -> list[str]:
                    cols = rule.get("columns")
                    if isinstance(cols, str):
                        cols = [c.strip() for c in cols.split(",") if c.strip()]
                        rule["columns"] = cols
                    if not isinstance(cols, list) or not cols or not all(str(c).strip() for c in cols):
                        raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' columns must be a non-empty list.")
                    cols = [str(c).strip() for c in cols]
                    rule["columns"] = cols
                    if count is not None and len(cols) != count:
                        raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' requires exactly {count} column(s).")
                    if minimum is not None and len(cols) < minimum:
                        raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' requires at least {minimum} column(s).")
                    return cols

                for i, rule in enumerate(rules):
                    if not isinstance(rule, dict):
                        raise ValueError(f"DQ rule at index {i} must be a dictionary.")
                    rule.setdefault("rule_id", f"dq_rule_{i + 1}")
                    rule.setdefault("severity", "warning")
                    rule.setdefault("description", "")
                    rule["rule_type"] = _canonical_dq_rule_type(rule.get("rule_type"))
                    rtype = rule["rule_type"]
                    if rtype not in DQ_RULE_TYPES:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported rule_type '{rtype}'.")
                    if str(rule.get("severity", "warning")).lower() not in {"warning", "error"}:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' severity must be warning or error.")

                    if rtype in {"not_null", "non_empty_string", "required_when"}:
                        require_columns(rule, minimum=1)
                    elif rtype in {
                        "null_rate_below", "unique", "accepted_values", "not_in_values", "between",
                        "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal",
                        "regex_match", "date_not_future", "date_between", "freshness", "max_age_days", "value_when",
                    }:
                        require_columns(rule, count=1)
                    elif rtype == "unique_combination":
                        require_columns(rule, minimum=2)
                    elif rtype in {"column_pair_equal", "column_a_gte_column_b", "column_a_gt_column_b"}:
                        require_columns(rule, count=2)
                    elif rtype == "expression_true":
                        if not str(rule.get("expression") or "").strip():
                            raise ValueError(f"DQ rule '{rule['rule_id']}' requires expression.")

                    if rtype == "null_rate_below" and rule.get("max_null_percent") is None:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires max_null_percent.")
                    if rtype == "accepted_values" and "allowed_values" not in rule:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires allowed_values.")
                    if rtype == "not_in_values" and "blocked_values" not in rule:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires blocked_values.")
                    if rtype in {"between", "date_between"} and rule.get("min_value") is None and rule.get("max_value") is None:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires min_value or max_value.")
                    if rtype in {"greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal"} and rule.get("value") is None:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires value.")
                    if rtype == "regex_match" and not str(rule.get("regex_pattern") or ""):
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires regex_pattern.")
                    if rtype in {"freshness", "max_age_days"} and rule.get("max_age_days") is None:
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires max_age_days.")
                    if rtype == "required_when" and not str(rule.get("condition") or "").strip():
                        raise ValueError(f"DQ rule '{rule['rule_id']}' requires condition.")
                    if rtype == "value_when":
                        if not str(rule.get("condition") or "").strip():
                            raise ValueError(f"DQ rule '{rule['rule_id']}' requires condition.")
                        if "expected_value" not in rule:
                            raise ValueError(f"DQ rule '{rule['rule_id']}' requires expected_value.")
                return rules
            ```

        ??? example "Validation helpers"

            **`def _dq_check_status(severity: str, failed_count: int) -> str`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1368-L1371)

            ```python
            def _dq_check_status(severity: str, failed_count: int) -> str:
                if failed_count <= 0:
                    return "passed"
                return "failed" if str(severity).strip().lower() == "error" else "warning"
            ```

            **`def _run_dq_guardrail_checks(df, table_name: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1374-L1409)

            ```python
            def _run_dq_guardrail_checks(df, table_name: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
                """Run DQ rules and return notebook guardrail check dictionaries."""
                _, F, _ = _spark_sql_helpers()
                _validate_dq_rules(rules)
                total = int(df.count())
                checks: list[dict[str, Any]] = []
                dataframe_columns = set(getattr(df, "columns", []))
                for rule in rules:
                    failed_rows = df.select(
                        F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0)).alias("failed")
                    )
                    failed_count = int(
                        failed_rows.agg(F.sum("failed").alias("failed_count")).collect()[0]["failed_count"] or 0
                    )
                    severity = str(rule.get("severity", "warning")).strip().lower()
                    columns = [str(column) for column in rule.get("columns", [])]
                    check_status = _dq_check_status(severity, failed_count)
                    check = {
                        "check": "dq_rule",
                        "table_name": table_name,
                        "rule_id": str(rule.get("rule_id") or ""),
                        "rule_type": str(rule.get("rule_type") or ""),
                        "columns": columns,
                        "severity": severity,
                        "status": check_status,
                        "passed": failed_count == 0,
                        "failed_count": failed_count,
                        "total_count": total,
                        "failed_percent": float(round((failed_count / total) * 100, 4)) if total else 0.0,
                        "description": str(rule.get("description") or ""),
                    }
                    missing_columns = [column for column in columns if column not in dataframe_columns]
                    if missing_columns:
                        check["missing_columns"] = missing_columns
                    checks.append(check)
                return checks
            ```

        ??? example "Rule parsing helpers"

            **`def _canonical_dq_rule_type(rule_type: Any) -> str`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L78-L79)

            ```python
            def _canonical_dq_rule_type(rule_type: Any) -> str:
                return str(rule_type or "").strip()
            ```

        ??? example "Rule evaluation helpers"

            **`def _dq_failed_expression(df, rule: dict[str, Any])`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1284-L1366)

            ```python
            def _dq_failed_expression(df, rule: dict[str, Any]):
                """Build a Spark boolean expression identifying rows that fail one DQ rule."""
                _, F, Window = _spark_sql_helpers()
                rule = _validate_dq_rules([dict(rule)])[0]
                rtype = str(rule["rule_type"])
                cols = [str(column) for column in rule.get("columns", [])]
                dataframe_columns = set(getattr(df, "columns", []))
                missing_columns = [column for column in cols if column not in dataframe_columns]
                expression = str(rule.get("expression") or "")
                if rtype != "expression_true" and missing_columns:
                    return F.lit(True)
                col_name = cols[0] if cols else None

                def empty_string(column: str):
                    return F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == "")

                def cast_for_compare(column):
                    return F.col(column)

                if rtype == "not_null":
                    failed = F.col(cols[0]).isNull()
                    for c in cols[1:]:
                        failed = failed | F.col(c).isNull()
                elif rtype == "null_rate_below":
                    total = int(df.count())
                    null_count = int(df.filter(F.col(col_name).isNull()).count()) if total else 0
                    failed = F.col(col_name).isNull() if total and ((null_count / total) * 100) > float(rule["max_null_percent"]) else F.lit(False)
                elif rtype == "non_empty_string":
                    failed = empty_string(cols[0])
                    for c in cols[1:]:
                        failed = failed | empty_string(c)
                elif rtype in {"unique", "unique_combination"}:
                    failed = F.count(F.lit(1)).over(Window.partitionBy(*[F.col(c) for c in cols])) > F.lit(1)
                elif rtype == "accepted_values":
                    failed = F.col(col_name).isNotNull() & ~F.col(col_name).isin(list(rule["allowed_values"]))
                elif rtype == "not_in_values":
                    failed = F.col(col_name).isNotNull() & F.col(col_name).isin(list(rule["blocked_values"]))
                elif rtype in {"between", "date_between"}:
                    value_col = cast_for_compare(col_name)
                    cond = F.lit(False)
                    if rule.get("min_value") is not None:
                        cond = cond | (value_col < F.lit(rule["min_value"]))
                    if rule.get("max_value") is not None:
                        cond = cond | (value_col > F.lit(rule["max_value"]))
                    failed = F.col(col_name).isNotNull() & cond
                elif rtype == "greater_than":
                    failed = F.col(col_name).isNotNull() & ~(F.col(col_name) > F.lit(rule["value"]))
                elif rtype == "greater_than_or_equal":
                    failed = F.col(col_name).isNotNull() & ~(F.col(col_name) >= F.lit(rule["value"]))
                elif rtype == "less_than":
                    failed = F.col(col_name).isNotNull() & ~(F.col(col_name) < F.lit(rule["value"]))
                elif rtype == "less_than_or_equal":
                    failed = F.col(col_name).isNotNull() & ~(F.col(col_name) <= F.lit(rule["value"]))
                elif rtype == "regex_match":
                    failed = F.col(col_name).isNotNull() & ~F.col(col_name).cast("string").rlike(rule["regex_pattern"])
                elif rtype == "date_not_future":
                    failed = F.col(col_name).isNotNull() & (F.to_date(F.col(col_name)) > F.current_date())
                elif rtype in {"freshness", "max_age_days"}:
                    failed = F.col(col_name).isNotNull() & (F.to_date(F.col(col_name)) < F.date_sub(F.current_date(), int(rule["max_age_days"])))
                elif rtype == "column_pair_equal":
                    failed = ~F.col(cols[0]).eqNullSafe(F.col(cols[1]))
                elif rtype == "column_a_gte_column_b":
                    one_null = F.col(cols[0]).isNull() != F.col(cols[1]).isNull()
                    both_non_null_and_invalid = F.col(cols[0]).isNotNull() & F.col(cols[1]).isNotNull() & ~(F.col(cols[0]) >= F.col(cols[1]))
                    failed = one_null | both_non_null_and_invalid
                elif rtype == "column_a_gt_column_b":
                    one_null = F.col(cols[0]).isNull() != F.col(cols[1]).isNull()
                    both_non_null_and_invalid = F.col(cols[0]).isNotNull() & F.col(cols[1]).isNotNull() & ~(F.col(cols[0]) > F.col(cols[1]))
                    failed = one_null | both_non_null_and_invalid
                elif rtype == "required_when":
                    condition = F.expr(str(rule["condition"]))
                    missing = empty_string(cols[0])
                    for c in cols[1:]:
                        missing = missing | empty_string(c)
                    failed = condition & missing
                elif rtype == "value_when":
                    condition = F.expr(str(rule["condition"]))
                    failed = condition & ~F.col(col_name).eqNullSafe(F.lit(rule["expected_value"]))
                elif rtype == "expression_true":
                    failed = ~F.expr(expression)
                else:
                    raise ValueError(f"Unsupported rule_type: {rtype}")
                return F.coalesce(failed, F.lit(False))
            ```

            **`def _dq_failed_row_count(df, rules: list[dict[str, Any]]) -> int`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1448-L1458)

            ```python
            def _dq_failed_row_count(df, rules: list[dict[str, Any]]) -> int:
                """Return the count of rows that failed at least one DQ rule."""
                _, F, _ = _spark_sql_helpers()
                if not rules:
                    return 0
                failed_columns = [F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0)) for rule in rules]
                failed_row = failed_columns[0]
                for column in failed_columns[1:]:
                    failed_row = failed_row + column
                failed_rows = df.select(F.when(failed_row > F.lit(0), F.lit(1)).otherwise(F.lit(0)).alias("failed"))
                return int(failed_rows.agg(F.sum("failed").alias("failed_count")).collect()[0]["failed_count"] or 0)
            ```

            **`def _dq_summary(checks: list[dict[str, Any]], total_count: int, failed_row_count: int, *, config: Any=None) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1461-L1476)

            ```python
            def _dq_summary(checks: list[dict[str, Any]], total_count: int, failed_row_count: int, *, config: Any = None) -> dict[str, Any]:
                """Build aggregate DQ fields for catalogue/profile evidence."""
                failed_checks = [check for check in checks if not bool(check.get("passed", False))]
                warning_checks = [check for check in failed_checks if check.get("severity") == "warning"]
                error_checks = [check for check in failed_checks if check.get("severity") == "error"]
                status = _summarize_dq_guardrail(checks)["status"]
                return {
                    "DQ_STATUS": status,
                    "DQ_RULE_COUNT": len(checks),
                    "DQ_FAILED_RULE_COUNT": len(failed_checks),
                    "DQ_WARNING_RULE_COUNT": len(warning_checks),
                    "DQ_ERROR_RULE_COUNT": len(error_checks),
                    "DQ_FAILED_ROW_COUNT": failed_row_count,
                    "DQ_FAILED_ROW_PERCENT": float(round((failed_row_count / total_count) * 100, 4)) if total_count else 0.0,
                    "DQ_CHECKED_AT": _current_audit_timestamp(config=config, drop_microseconds=False),
                }
            ```

            **`def _dq_tagged_dataframe(df, rules: list[dict[str, Any]])`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1412-L1445)

            ```python
            def _dq_tagged_dataframe(df, rules: list[dict[str, Any]]):
                """Return the full DataFrame tagged with failed DQ rule IDs and row status."""
                _, F, _ = _spark_sql_helpers()
                sorted_rules = sorted(rules or [], key=lambda rule: str(rule.get("rule_id") or ""))
                failed_rule_columns = [
                    F.when(_dq_failed_expression(df, rule), F.lit(str(rule.get("rule_id") or "")))
                    for rule in sorted_rules
                ]
                failed_rules = F.concat_ws(",", *failed_rule_columns) if failed_rule_columns else F.lit("")
                error_failures = [
                    F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0))
                    for rule in sorted_rules
                    if str(rule.get("severity", "warning")).strip().lower() == "error"
                ]
                warning_failures = [
                    F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0))
                    for rule in sorted_rules
                    if str(rule.get("severity", "warning")).strip().lower() != "error"
                ]
                error_count = error_failures[0] if error_failures else F.lit(0)
                for failure in error_failures[1:]:
                    error_count = error_count + failure
                warning_count = warning_failures[0] if warning_failures else F.lit(0)
                for failure in warning_failures[1:]:
                    warning_count = warning_count + failure
                return (
                    df.withColumn("_dq_failed_rules", failed_rules)
                    .withColumn(
                        "_dq_check_status",
                        F.when(error_count > F.lit(0), F.lit("failed"))
                        .when(warning_count > F.lit(0), F.lit("warning"))
                        .otherwise(F.lit("passed")),
                    )
                )
            ```

            **`def _spark_sql_helpers()`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1083-L1090)

            ```python
            def _spark_sql_helpers():
                """Return Spark SQL helper modules lazily for DQ runtime helpers."""
                try:
                    from pyspark.sql import SparkSession, functions as F
                    from pyspark.sql.window import Window
                except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
                    raise RuntimeError("DQ enforcement helpers require pyspark in the active runtime.") from exc
                return SparkSession, F, Window
            ```

            **`def _summarize_dq_guardrail(checks: list[dict[str, Any]]) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1479-L1496)

            ```python
            def _summarize_dq_guardrail(checks: list[dict[str, Any]]) -> dict[str, Any]:
                if any(check.get("status") == "failed" for check in checks):
                    status = "failed"
                    can_continue = False
                elif any(check.get("status") == "warning" for check in checks):
                    status = "warning"
                    can_continue = True
                else:
                    status = "passed"
                    can_continue = True
                failed_checks = [check for check in checks if check.get("status") in {"warning", "failed"}]
                if not checks:
                    message = "No active approved DQ rules found."
                elif failed_checks:
                    message = f"DQ guardrail found {len(failed_checks)} rule failure(s): {status}."
                else:
                    message = f"DQ guardrail passed {len(checks)} active approved rule(s)."
                return {"status": status, "can_continue": can_continue, "checks": checks, "message": message}
            ```

        ??? example "Other helpers"

            **`def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L62-L67)

            ```python
            def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
                if rows_or_df is None:
                    return []
                if hasattr(rows_or_df, "collect"):
                    rows_or_df = rows_or_df.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
            ```


## Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

## Source link

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1499-L1556">View enforce_dq_rules on GitHub</a>

```python
def enforce_dq_rules(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    *,
    spark_session=None,
) -> dict:
    """Enforce active approved DQ rules as a simple pipeline guardrail.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame to evaluate before the target write. The full DataFrame
        is never filtered or split by this helper.
    config : FrameworkConfig or dict
        Runtime configuration containing the configured metadata lakehouse
        route from ``00_env_config``.
    env : str
        Environment name used to read ``METADATA_DQ_RULES`` from the configured
        metadata target.
    dataset_name : str
        Dataset identifier used with ``table_name`` to scope approved DQ rules
        when those columns exist in the metadata table.
    table_name : str
        Target table name whose approved active DQ rules should be enforced.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used to read metadata when required by the configured
        storage helper.

    Returns
    -------
    dict
        Guardrail result with ``status``, ``can_continue``, ``checks``, and
        ``message``. The result also carries the full tagged ``dataframe`` and
        aggregate ``summary`` fields for the existing catalogue evidence path.
        Error-severity rule failures return ``status='failed'`` and
        ``can_continue=False``. Warning-severity failures return
        ``status='warning'`` and ``can_continue=True``. Passing or absent rules
        return ``status='passed'`` and ``can_continue=True``.

    Notes
    -----
    This v1 guardrail reads approved active rules from ``METADATA_DQ_RULES`` via
    the configured metadata route. It records aggregate rule outcomes only; it
    does not quarantine rows, write row-level failure metadata, filter invalid
    rows, send alerts, or partially write targets.
    """
    metadata_df = read_lakehouse_table(config, env, "metadata", DQ_RULES_TABLE, spark_session=spark_session)
    rules = _load_active_dq_rules(metadata_df, table_name=table_name, env_name=env, dataset_name=dataset_name)
    checks = _run_dq_guardrail_checks(dataframe, table_name=table_name, rules=rules) if rules else []
    total_count = int(dataframe.count())
    failed_row_count = _dq_failed_row_count(dataframe, rules) if rules else 0
    result = _summarize_dq_guardrail(checks)
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules)
    result["summary"] = _dq_summary(checks, total_count, failed_row_count, config=config)
    return result
```

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.enforce_dq_rules`
- Short name: `enforce_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1499`
- Inbound references count: 1
- Outbound references count: 7
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: guardrail, can_continue, catalogue evidence, metadata lakehouse

### AI implementation contract

- **required_context:** Requires active approved DQ-rule evidence in the configured metadata target from 03_governance governance workflows.
- **inputs:** dataframe, config, env, dataset_name, table_name, and optional spark_session.
- **output:** Guardrail result dictionary with status, can_continue, checks, message, tagged dataframe, and summary fields.
- **side_effects:** Reads approved DQ-rule metadata and evaluates checks against the DataFrame; it does not filter the DataFrame or write target data.
- **failure_modes:** Raises configuration, metadata-read, or Spark expression errors when approved rules cannot be loaded or evaluated.
- **verification:** Verify approved metadata exists, inspect status/can_continue, and call stop_if_failed before writing when blocking failures occur.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._dq_failed_row_count`
- `fabricops_kit.governance_review._dq_summary`
- `fabricops_kit.governance_review._dq_tagged_dataframe`
- `fabricops_kit.governance_review._load_active_dq_rules`
- `fabricops_kit.governance_review._run_dq_guardrail_checks`
- `fabricops_kit.governance_review._summarize_dq_guardrail`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1499-L1556">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L1499-L1556</a>
- Start line: `1499`
- End line: `1556`
- Signature:

```python
def enforce_dq_rules(dataframe, config, env, dataset_name, table_name, *, spark_session=None) -> dict
```

### Internal relationship graph

### Public related functions

- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 16
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
