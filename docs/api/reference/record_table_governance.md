# record_table_governance

## Signature

```python
def record_table_governance(config: Any, env: str, profile_rows: list[dict[str, Any]], *, spark_session: Any, context_reviews: list[dict[str, Any]] | None=None, dq_rule_reviews: list[dict[str, Any]] | None=None, classification_reviews: list[dict[str, Any]] | None=None, approved_by: str | None=None, governance_selection: dict[str, Any] | None=None, write_governance_review: bool=False, mode: str='append') -> dict[str, Any]
```

## Summary

Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.

## Usage note

- Use after reviewers approve governance rows in 03_governance and those approvals should become metadata-backed evidence.

**Do not use when:**

- Do not use to draft governance recommendations, bypass review approval, or write unapproved rows.

**Additional context:**

Persists approved column context, DQ rules, and classification records for a selected table in one governance commit action.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `Any` | Yes | Shared ``00_env_config`` configuration that routes metadata writes to the configured metadata lakehouse target. |
| `env` | `str` | Yes | Environment key in ``config``. |
| `profile_rows` | `list[dict[str, Any]]` | Yes | Column-profile rows loaded for the selected catalogue table. |
| `spark_session` | `Any` | Yes | Spark session used to create DataFrames for metadata writes. |
| `context_reviews` | `list[dict[str, Any]] \| None` | No | Human-approved rows from the governance review workflow. Only rows with ``review_status="approved"`` and ``commit=True`` are written. |
| `dq_rule_reviews` | `list[dict[str, Any]] \| None` | No | Not documented yet |
| `classification_reviews` | `list[dict[str, Any]] \| None` | No | Not documented yet |
| `approved_by` | `str \| None` | No | Reviewer identity to stamp on records. When omitted, runtime defaults are used. |
| `governance_selection` | `dict[str, Any] \| None` | No | Catalogue selection used to re-read persisted evidence and write a final governance outcome row. |
| `write_governance_review` | `bool` | No | Whether to append a ``METADATA_GOVERNANCE_REVIEWS`` outcome row after checking agreement, pipeline, schema/profile, and DQ evidence. |
| `mode` | `str` | No | Write mode for metadata table commits. |

## Returns

Dictionary of records written for column_context, dq_rules, and column_classification.

### Return interpretation

The returned dictionary groups written records by metadata area. Confirm counts match approved review rows before treating governance as complete.

## Raises / Errors

Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.

### Common failure causes

- Review rows are not approved.
- Required profile context is missing.
- Metadata routing is unavailable.
- Spark cannot write one of the governance metadata tables.

## Example

```python
written = record_table_governance(CONFIG, env, profile_rows, spark_session=spark, context_reviews=context_rows, dq_rule_reviews=dq_rows, classification_reviews=classification_rows, approved_by="reviewer")
```

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)

**Glossary terms**

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## Developer details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `978`
- Signature:

```python
def record_table_governance(config: Any, env: str, profile_rows: list[dict[str, Any]], *, spark_session: Any, context_reviews: list[dict[str, Any]] | None=None, dq_rule_reviews: list[dict[str, Any]] | None=None, classification_reviews: list[dict[str, Any]] | None=None, approved_by: str | None=None, governance_selection: dict[str, Any] | None=None, write_governance_review: bool=False, mode: str='append') -> dict[str, Any]
```

**Used in templates:**

- `03_governance`

**Side effects:**

Writes approved governance metadata records to configured metadata tables.

**Notes:**

This is the v1 governance commit action for ``03_governance`` notebooks. It merges
the previous row-builder and per-table commit helpers into one explicit
human approval step while preserving configured metadata lakehouse routing.

## Calls

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.governance_review._build_classification_records`
- `fabricops_kit.governance_review._build_column_context_records`
- `fabricops_kit.governance_review._build_dq_rule_records`
- `fabricops_kit.governance_review._review_governance_evidence`

## Internal implementation summary

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in the internal implementation summary.

    ```text
    record_table_governance(...)
    ├── _build_classification_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   └── _json(...)
    ├── _build_column_context_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   └── _json(...)
    ├── _build_dq_rule_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   ├── _build_dq_rule_key(...)
    │   │   └── …
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _dq_rule_parameter_payload(...)
    │   ├── _json(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _review_governance_evidence(...)
    │   ├── _build_metadata_table_key(...)
    │   │   └── …
    │   ├── _build_runtime_audit_fields(...)
    │   │   └── …
    │   ├── _latest_row(...)
    │   │   └── …
    │   ├── _now_utc_iso(...)
    │   │   └── …
    │   ├── _read_metadata_rows(...)
    │   │   └── …
    │   ├── _resolve_action_by(...)
    │   │   └── …
    │   ├── _status_is_failed(...)
    │   ├── _status_is_warning(...)
    │   ├── _value(...)
    │   ├── load_catalogue_profile_rows(...)
    │   │   └── …
    │   └── write_lakehouse_table(...)
    │       └── …
    └── write_lakehouse_table(...)
        ├── _get_store(...)
        ├── _normalize_table_name(...)
        ├── _registered_table_identifier(...)
        │   └── …
        └── _uses_registered_metadata_table(...)
    ```

??? info "Internal helpers used: 29"

    This callable uses 29 internal helpers for audit timestamp, metadata loading, rule parsing, rule evaluation, result summary, and other.

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
          <td data-label="Helpers"><code>_build_runtime_audit_fields</code>, <code>_current_audit_timestamp</code>, <code>_get_audit_timezone</code>, <code>_latest_row</code>, <code>_validate_audit_timezone</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_build_metadata_column_key</code>, <code>_build_metadata_table_key</code>, <code>_dq_rule_parameter_payload</code>, <code>_read_metadata_rows</code>, <code>_stable_metadata_key</code>, <code>_validate_dq_rules</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_canonical_dq_rule_type</code>, <code>_json</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule evaluation</td>
          <td data-label="Helpers"><code>_build_dq_rule_key</code>, <code>_build_dq_rule_records</code></td>
          <td data-label="What they do">Convert configured rules into executable checks and evaluation results.</td>
        </tr>
        <tr>
          <td data-label="Area">Result summary</td>
          <td data-label="Helpers"><code>_status_is_failed</code>, <code>_status_is_warning</code></td>
          <td data-label="What they do">Build final statuses, counts, and messages for the caller.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_approved_column_identity</code>, <code>_approved_review_context</code>, <code>_build_classification_records</code>, <code>_build_column_context_records</code>, <code>_coerce_rows</code>, <code>_context_get</code>, <code>_now_utc_iso</code>, <code>_resolve_action_by</code>, <code>_review_governance_evidence</code>, <code>_runtime_context</code>, <code>_safe_str</code>, <code>_value</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _build_runtime_audit_fields(*, config: Any=None, env: str | None=None, timestamp_field: str='_committed_at', user_field: str='_committed_by', workspace_field: str='_workspace_name', notebook_field: str='_notebook_name', metadata_lakehouse_field: str='_metadata_lakehouse_name', activity_field: str='_activity_id', committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, str]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L147-L217)

            ```python
            def _build_runtime_audit_fields(
                *,
                config: Any = None,
                env: str | None = None,
                timestamp_field: str = "_committed_at",
                user_field: str = "_committed_by",
                workspace_field: str = "_workspace_name",
                notebook_field: str = "_notebook_name",
                metadata_lakehouse_field: str = "_metadata_lakehouse_name",
                activity_field: str = "_activity_id",
                committed_by: str | None = None,
                committed_at: str | None = None,
                runtime_context: dict[str, Any] | None = None,
            ) -> dict[str, str]:
                """Build reusable framework-managed audit fields for metadata-table rows.

                Parameters
                ----------
                config : FrameworkConfig | dict, optional
                    Framework config containing ``path_config.paths[env]["metadata"]``.
                env : str, optional
                    Environment key paired with ``config``.
                timestamp_field, user_field, workspace_field, notebook_field : str
                    Output keys for timestamp, user, workspace, and notebook audit values.
                metadata_lakehouse_field, activity_field : str
                    Output keys for metadata lakehouse and Fabric activity audit values.
                committed_by, committed_at : str, optional
                    Deterministic audit overrides. When omitted, values resolve from Fabric
                    runtime context and the configured audit timezone timestamp.
                runtime_context : dict[str, Any], optional
                    Values merged over :func:`_runtime_context`, primarily for tests or
                    controlled notebook overrides.

                Returns
                -------
                dict[str, str]
                    Framework-managed metadata audit values keyed by the supplied field
                    names.

                Notes
                -----
                DataFrame runtime audit columns and metadata-table audit fields both use
                underscore-prefixed names. This helper centralizes the metadata-table
                convention so notebooks can reuse runtime context when adding dataframe
                audit columns inline.
                """
                context = {**_runtime_context(), **(runtime_context or {})}

                def _first_non_blank(*keys: str) -> Any:
                    for key in keys:
                        value = _context_get(context, key)
                        if value is not None and str(value).strip():
                            return value
                    return None

                metadata_lakehouse_name = ""
                if config is not None and env is not None:
                    paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
                    metadata_lakehouse_name = _safe_str(paths[env]["metadata"].name)
                return {
                    user_field: _safe_str(committed_by).strip()
                    if committed_by and _safe_str(committed_by).strip()
                    else _safe_str(_first_non_blank("userName", "userId") or "unknown"),
                    timestamp_field: _safe_str(committed_at)
                    if committed_at
                    else _current_audit_timestamp(config=config),
                    workspace_field: _safe_str(_first_non_blank("currentWorkspaceName", "workspaceName") or ""),
                    notebook_field: _safe_str(_first_non_blank("currentNotebookName", "notebookName") or ""),
                    metadata_lakehouse_field: metadata_lakehouse_name,
                    activity_field: _safe_str(_first_non_blank("activityId") or ""),
                }
            ```

            **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/config.py#L69-L75)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/config.py#L61-L66)

            ```python
            def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
                """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
                if timezone_name is not None:
                    return _validate_audit_timezone(timezone_name)
                value = getattr(config, "audit_timezone", None) if config is not None else None
                return _validate_audit_timezone(value)
            ```

            **`def _latest_row(rows: list[dict[str, Any]], *order_fields: str) -> dict[str, Any] | None`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L811-L815)

            ```python
            def _latest_row(rows: list[dict[str, Any]], *order_fields: str) -> dict[str, Any] | None:
                """Return the latest row using lexicographic string timestamps/ids."""
                if not rows:
                    return None
                return max(rows, key=lambda row: tuple(str(_value(row, field)) for field in order_fields))
            ```

            **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/config.py#L27-L58)

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

            **`def _build_metadata_column_key(environment_name, dataset_name, table_name, column_name) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L81-L82)

            ```python
            def _build_metadata_column_key(environment_name, dataset_name, table_name, column_name) -> str:
                return _stable_metadata_key(environment_name, dataset_name, table_name, column_name)
            ```

            **`def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L77-L78)

            ```python
            def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
                return _stable_metadata_key(environment_name, dataset_name, table_name)
            ```

            **`def _dq_rule_parameter_payload(rule: dict[str, Any], columns: list[str]) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L388-L410)

            ```python
            def _dq_rule_parameter_payload(rule: dict[str, Any], columns: list[str]) -> dict[str, Any]:
                """Return rule parameters stored inside ``rule_parameters_json``."""
                metadata_fields = {
                    "rule_key", "rule_id", "metadata_column_key", "metadata_table_key", "environment_name", "dataset_name",
                    "table_name", "column_name", "rule_type", "rule_parameters", "rule_parameters_json", "severity",
                    "description", "is_active", "review_status", "approved_by", "approved_at", "ai_suggestion_json",
                    "ai_suggestion", "action_type", "commit", "_committed_at", "_committed_by", "_workspace_name",
                    "_notebook_name", "_metadata_lakehouse_name", "_activity_id",
                }
                payload: dict[str, Any] = {"columns": columns}
                raw = rule.get("rule_parameters") or rule.get("rule_parameters_json") or {}
                if isinstance(raw, str) and raw.strip():
                    try:
                        raw = json.loads(raw)
                    except Exception:
                        raw = {}
                if isinstance(raw, dict):
                    payload.update(raw)
                for key, value in rule.items():
                    if key not in metadata_fields and value is not None:
                        payload[key] = value
                payload["columns"] = columns
                return payload
            ```

            **`def _read_metadata_rows(config: Any, env: str, table: str, *, spark_session: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L826-L827)

            ```python
            def _read_metadata_rows(config: Any, env: str, table: str, *, spark_session: Any) -> list[dict[str, Any]]:
                return _coerce_rows(read_lakehouse_table(config, env, "metadata", table, spark_session=spark_session))
            ```

            **`def _stable_metadata_key(*parts: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L72-L74)

            ```python
            def _stable_metadata_key(*parts: Any) -> str:
                normalized = "|".join(str(part or "").strip().lower() for part in parts)
                return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            ```

            **`def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L1146-L1219)

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

        ??? example "Rule parsing helpers"

            **`def _canonical_dq_rule_type(rule_type: Any) -> str`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L78-L79)

            ```python
            def _canonical_dq_rule_type(rule_type: Any) -> str:
                return str(rule_type or "").strip()
            ```

            **`def _json(value: Any) -> str`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L489-L494)

            ```python
            def _json(value: Any) -> str:
                if value in (None, ""):
                    return ""
                if isinstance(value, str):
                    return value
                return json.dumps(value, sort_keys=True)
            ```

        ??? example "Rule evaluation helpers"

            **`def _build_dq_rule_key(environment_name, dataset_name, table_name, rule_id) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L85-L86)

            ```python
            def _build_dq_rule_key(environment_name, dataset_name, table_name, rule_id) -> str:
                return _stable_metadata_key(environment_name, dataset_name, table_name, rule_id)
            ```

            **`def _build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any=None, env: str | None=None, approved_by: str | None=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L413-L464)

            ```python
            def _build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
                """Build append-only approved DQ-rule records without enforcing them."""
                profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
                rows = []
                for rule in reviewed_rules or []:
                    if not rule.get("commit"):
                        continue
                    review_status = str(rule.get("review_status", "approved")).lower()
                    action_type = str(rule.get("action_type") or ("created" if rule.get("is_active", True) else "deactivated")).lower()
                    if action_type == "delete":
                        action_type = "deactivated"
                    if action_type not in {"created", "updated", "deactivated", "reactivated", "approved"}:
                        raise ValueError(f"Unsupported DQ action_type: {action_type}")
                    is_active = bool(rule.get("is_active", action_type != "deactivated"))
                    if action_type == "deactivated":
                        is_active = False
                    if action_type == "reactivated":
                        is_active = True
                    if review_status != "approved":
                        continue
                    draft = dict(rule)
                    draft["rule_type"] = _canonical_dq_rule_type(draft.get("rule_type"))
                    if draft["rule_type"] != "expression_true":
                        columns = draft.get("columns") or ([draft.get("column_name")] if draft.get("column_name") else [])
                        if isinstance(columns, str):
                            columns = [c.strip() for c in columns.split(",") if c.strip()]
                        draft["columns"] = list(columns or [])
                    _validate_dq_rules([draft])
                    columns = [str(c) for c in draft.get("columns", [])]
                    display_column = str(rule.get("column_name") or ", ".join(columns) or "")
                    primary_column = columns[0] if columns else display_column
                    identity = _approved_column_identity(profile.get(primary_column, {}), {**rule, "column_name": display_column, "columns": columns}, env=env)
                    identity["column_name"] = display_column
                    rule_id = str(rule.get("rule_id") or f"{identity['table_name']}.{display_column or 'table'}.{draft['rule_type']}")
                    params = _dq_rule_parameter_payload(draft, columns)
                    rows.append({
                        "rule_key": str(rule.get("rule_key") or _build_dq_rule_key(identity["environment_name"], identity["dataset_name"], identity["table_name"], rule_id)),
                        "rule_id": rule_id,
                        **identity,
                        "rule_type": draft["rule_type"],
                        "rule_parameters_json": _json(params),
                        "severity": str(rule.get("severity") or "warning").lower(),
                        "description": str(rule.get("description") or ""),
                        "is_active": is_active,
                        "review_status": "approved",
                        "approved_by": str(rule.get("approved_by") or actor),
                        "approved_at": str(rule.get("approved_at") or now),
                        "ai_suggestion_json": _json(rule.get("ai_suggestion_json") or rule.get("ai_suggestion")),
                        "action_type": action_type,
                        **audit,
                    })
                return rows
            ```

        ??? example "Result summary helpers"

            **`def _status_is_failed(value: Any) -> bool`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L818-L819)

            ```python
            def _status_is_failed(value: Any) -> bool:
                return str(value or "").strip().lower() in {"failed", "fail", "error", "errors", "rejected"}
            ```

            **`def _status_is_warning(value: Any) -> bool`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L822-L823)

            ```python
            def _status_is_warning(value: Any) -> bool:
                return str(value or "").strip().lower() in {"warning", "warnings", "needs_remediation", "drift"}
            ```

        ??? example "Other helpers"

            **`def _approved_column_identity(profile_row: dict[str, Any], review_row: dict[str, Any], *, env: str | None=None) -> dict[str, str]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L88-L100)

            ```python
            def _approved_column_identity(profile_row: dict[str, Any], review_row: dict[str, Any], *, env: str | None = None) -> dict[str, str]:
                col = str(review_row.get("column_name") or _value(profile_row, "column_name") or ((review_row.get("columns") or [""])[0]))
                env_name = str(_value(profile_row, "environment_name") or review_row.get("environment_name") or env or "")
                dataset = str(_value(profile_row, "dataset_name") or review_row.get("dataset_name") or "")
                table = str(_value(profile_row, "table_name") or review_row.get("table_name") or "")
                return {
                    "metadata_column_key": str(_value(profile_row, "metadata_column_key") or review_row.get("metadata_column_key") or _build_metadata_column_key(env_name, dataset, table, col)),
                    "metadata_table_key": str(_value(profile_row, "metadata_table_key") or review_row.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset, table)),
                    "environment_name": env_name,
                    "dataset_name": dataset,
                    "table_name": table,
                    "column_name": col,
                }
            ```

            **`def _approved_review_context(profile_rows: list[dict[str, Any]], *, config: Any=None, env: str | None=None, approved_by: str | None=None) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L82-L85)

            ```python
            def _approved_review_context(profile_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]:
                actor = _resolve_action_by(approved_by)
                audit = _build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
                return {str(_value(r, "column_name")): r for r in profile_rows}, actor, _now_utc_iso(config), audit
            ```

            **`def _build_classification_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any=None, env: str | None=None, approved_by: str | None=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L466-L487)

            ```python
            def _build_classification_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
                """Build append-only approved sensitivity and PII classification records."""
                profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
                rows = []
                for review in reviewed_rows or []:
                    if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
                        continue
                    sensitivity = str(review.get("sensitivity_label") or "internal")
                    classification = str(review.get("personal_data_classification") or "unknown")
                    if sensitivity not in SENSITIVITY_LABELS:
                        raise ValueError(f"Unsupported sensitivity_label: {sensitivity}")
                    if classification not in PERSONAL_DATA_CLASSIFICATIONS:
                        raise ValueError(f"Unsupported personal_data_classification: {classification}")
                    identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
                    rows.append({
                        **identity,
                        "sensitivity_label": sensitivity, "personal_data_classification": classification,
                        "pii_identifier_type": str(review.get("pii_identifier_type") or ""), "handling_requirement": str(review.get("handling_requirement") or ""),
                        "reasoning": str(review.get("reasoning") or ""), "review_status": "approved", "approved_by": actor, "approved_at": now,
                        "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
                    })
                return rows
            ```

            **`def _build_column_context_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any=None, env: str | None=None, approved_by: str | None=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L372-L385)

            ```python
            def _build_column_context_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
                """Build append-only approved business-context records from explicit reviews."""
                profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
                rows = []
                for review in reviewed_rows or []:
                    if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
                        continue
                    identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
                    rows.append({
                        **identity,
                        "business_context": str(review.get("business_context") or ""), "notes": str(review.get("notes") or ""), "review_status": "approved",
                        "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
                    })
                return rows
            ```

            **`def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L62-L67)

            ```python
            def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
                if rows_or_df is None:
                    return []
                if hasattr(rows_or_df, "collect"):
                    rows_or_df = rows_or_df.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
            ```

            **`def _context_get(context: Any, *keys: str) -> Any`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L101-L113)

            ```python
            def _context_get(context: Any, *keys: str) -> Any:
                for key in keys:
                    try:
                        if isinstance(context, dict):
                            value = context.get(key)
                        else:
                            getter = getattr(context, "get", None)
                            value = getter(key) if callable(getter) else None
                    except Exception:
                        value = None
                    if value is not None:
                        return value
                return None
            ```

            **`def _now_utc_iso(config: Any=None) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L61-L62)

            ```python
            def _now_utc_iso(config: Any = None) -> str:
                return _current_audit_timestamp(config=config, drop_microseconds=False)
            ```

            **`def _resolve_action_by(action_by: str | None=None) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L65-L69)

            ```python
            def _resolve_action_by(action_by: str | None = None) -> str:
                if action_by:
                    return str(action_by)
                context = _runtime_context()
                return str(_context_get(context, "userName", "userId") or "unknown")
            ```

            **`def _review_governance_evidence(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any, reviewed_by: str | None=None, mode: str='append') -> dict[str, Any]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L830-L976)

            ```python
            def _review_governance_evidence(
                config: Any,
                env: str,
                selection: dict[str, Any],
                *,
                spark_session: Any,
                reviewed_by: str | None = None,
                mode: str = "append",
            ) -> dict[str, Any]:
                """Review persisted v1 evidence and write a governance outcome row.

                Parameters
                ----------
                config : FrameworkConfig or dict
                    Shared ``00_env_config`` configuration used for metadata lakehouse routing.
                env : str
                    Environment key in ``config``.
                selection : dict[str, Any]
                    Catalogue-table selection returned by ``get_selected_catalogue_table``.
                spark_session : pyspark.sql.SparkSession
                    Spark session used to read and write metadata tables.
                reviewed_by : str, optional
                    Reviewer identity. Runtime user metadata is used when omitted.
                mode : str, default="append"
                    Write mode for ``METADATA_GOVERNANCE_REVIEWS``.

                Returns
                -------
                dict[str, Any]
                    Governance review row plus blocker, warning, and evidence details.

                Notes
                -----
                The function intentionally re-reads agreement, catalogue, pipeline-run, and
                evidence metadata from the configured ``metadata`` target so ``03_governance``
                can run in a separate session after ``02_pipeline``.
                """
                profile_rows = load_catalogue_profile_rows(config, env, selection, spark_session=spark_session)
                first_profile = profile_rows[0]
                env_name = str(_value(first_profile, "environment_name") or selection.get("environment_name") or env)
                dataset_name = str(_value(first_profile, "dataset_name") or selection.get("dataset_name") or "")
                table_name = str(_value(first_profile, "table_name") or selection.get("table_name") or "")
                table_key = str(_value(first_profile, "metadata_table_key") or selection.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset_name, table_name))
                profile_run_id = str(_value(first_profile, "profile_run_id") or selection.get("profile_run_id") or "")
                profile_stage = str(_value(first_profile, "profile_stage") or selection.get("profile_stage") or "")
                agreement_id = str(_value(first_profile, "agreement_id") or _value(first_profile, "AGREEMENT_ID") or "")
                agreement_contract_version = str(_value(first_profile, "contract_version") or _value(first_profile, "AGREEMENT_CONTRACT_VERSION") or "")

                all_pipeline_rows = [
                    row for row in _read_metadata_rows(config, env, PIPELINE_RUNS_TABLE, spark_session=spark_session)
                    if str(_value(row, "environment_name")) == env_name
                ]
                related_pipeline_rows = [
                    row for row in all_pipeline_rows
                    if not agreement_id or str(_value(row, "agreement_id")) == agreement_id
                ]
                pipeline_rows = [
                    row for row in related_pipeline_rows
                    if not profile_run_id or str(_value(row, "run_id")) == profile_run_id
                ]
                latest_pipeline = _latest_row(pipeline_rows, "completed_at", "created_at", "run_id")

                agreement_rows = [
                    row for row in _read_metadata_rows(config, env, DATA_AGREEMENT_TABLE, spark_session=spark_session)
                    if agreement_id and str(_value(row, "agreement_id")) == agreement_id
                    and (not agreement_contract_version or str(_value(row, "contract_version")) == agreement_contract_version)
                ]
                attachment_rows = [
                    row for row in _read_metadata_rows(config, env, DATA_AGREEMENT_EVIDENCE_TABLE, spark_session=spark_session)
                    if agreement_id and str(_value(row, "agreement_id")) == agreement_id
                    and (not agreement_contract_version or str(_value(row, "contract_version")) == agreement_contract_version)
                ]

                blockers: list[dict[str, str]] = []
                warnings: list[dict[str, str]] = []

                def _append_once(items: list[dict[str, str]], *, code: str, message: str) -> None:
                    if not any(item.get("code") == code for item in items):
                        items.append({"code": code, "message": message})

                if not agreement_id:
                    _append_once(blockers, code="missing_agreement_id", message="Catalogue evidence is not linked to an agreement.")
                elif not agreement_rows:
                    _append_once(blockers, code="missing_agreement_metadata", message="No matching agreement metadata row was found.")
                if latest_pipeline is None:
                    _append_once(blockers, code="missing_pipeline_run", message="No matching pipeline run summary was found.")
                elif _status_is_failed(_value(latest_pipeline, "status")):
                    _append_once(blockers, code="pipeline_failed", message="Latest pipeline run did not complete successfully.")

                dq_statuses = {str(_value(row, "dq_status") or "").lower() for row in profile_rows}
                dq_error_count = sum(int(_value(row, "dq_error_rule_count", 0) or 0) for row in profile_rows)
                dq_failed_count = sum(int(_value(row, "dq_failed_rule_count", 0) or 0) for row in profile_rows)
                if "failed" in dq_statuses or dq_error_count > 0:
                    _append_once(blockers, code="dq_failed", message="Failed DQ evidence blocks approval.")
                elif "warning" in dq_statuses or dq_failed_count > 0:
                    _append_once(warnings, code="dq_warning", message="DQ warning evidence requires remediation review.")

                if latest_pipeline is not None:
                    pipeline_dq_status = _value(latest_pipeline, "dq_status")
                    if _status_is_failed(pipeline_dq_status):
                        _append_once(blockers, code="dq_failed", message="Pipeline DQ status blocks approval.")
                    elif _status_is_warning(pipeline_dq_status):
                        _append_once(warnings, code="dq_warning", message="Pipeline DQ status requires remediation review.")

                    for field in ("source_guardrail_status", "target_guardrail_status"):
                        status = _value(latest_pipeline, field)
                        if _status_is_failed(status):
                            blockers.append({"code": f"{field}_failed", "message": f"{field} is {status}; schema drift or guardrail failure is present."})
                        elif _status_is_warning(status):
                            warnings.append({"code": f"{field}_warning", "message": f"{field} is {status}; schema drift is surfaced for review."})

                outcome = "rejected" if blockers else ("needs_remediation" if warnings else "approved")
                reviewed_at = _now_utc_iso(config)
                actor = _resolve_action_by(reviewed_by)
                audit = _build_runtime_audit_fields(config=config, env=env, committed_by=actor, committed_at=reviewed_at)
                evidence_summary = {
                    "agreement_row_count": len(agreement_rows),
                    "agreement_attachment_count": len(attachment_rows),
                    "profile_column_count": len(profile_rows),
                    "pipeline_run_count": len(pipeline_rows),
                    "related_pipeline_run_count": len(related_pipeline_rows),
                    "prior_pipeline_run_ids": [str(_value(row, "run_id")) for row in related_pipeline_rows if str(_value(row, "run_id")) != profile_run_id],
                    "latest_pipeline_run": latest_pipeline or {},
                }
                row = {
                    "review_id": f"{profile_run_id or 'profile'}-{uuid.uuid4().hex[:12]}",
                    "environment_name": env_name,
                    "dataset_name": dataset_name,
                    "table_name": table_name,
                    "metadata_table_key": table_key,
                    "profile_run_id": profile_run_id,
                    "profile_stage": profile_stage,
                    "pipeline_run_id": str(_value(latest_pipeline or {}, "run_id")),
                    "agreement_id": agreement_id,
                    "agreement_contract_version": agreement_contract_version,
                    "outcome": outcome,
                    "blocker_count": len(blockers),
                    "warning_count": len(warnings),
                    "blockers_json": json.dumps(blockers, sort_keys=True),
                    "warnings_json": json.dumps(warnings, sort_keys=True),
                    "evidence_summary_json": json.dumps(evidence_summary, default=str, sort_keys=True),
                    "reviewed_at": reviewed_at,
                    "reviewed_by": actor,
                    **audit,
                }
                write_lakehouse_table(spark_session.createDataFrame([row]), config, env, "metadata", GOVERNANCE_REVIEWS_TABLE, mode=mode)
                return {"review": row, "outcome": outcome, "blockers": blockers, "warnings": warnings, "evidence_summary": evidence_summary}
            ```

            **`def _runtime_context() -> dict[str, Any]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L120-L144)

            ```python
            def _runtime_context() -> dict[str, Any]:
                try:
                    import notebookutils  # type: ignore
                except Exception:
                    return {}

                runtime = getattr(notebookutils, "runtime", None)
                context = getattr(runtime, "context", None)
                if context is None:
                    return {}

                keys = [
                    "currentWorkspaceId",
                    "currentWorkspaceName",
                    "currentNotebookId",
                    "currentNotebookName",
                    "workspaceId",
                    "workspaceName",
                    "notebookId",
                    "notebookName",
                    "userId",
                    "userName",
                    "activityId",
                ]
                return {key: _context_get(context, key) for key in keys}
            ```

            **`def _safe_str(value: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L116-L117)

            ```python
            def _safe_str(value: Any) -> str:
                return "" if value is None else str(value)
            ```

            **`def _value(row: dict[str, Any], name: str, default: Any='') -> Any`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L70-L71)

            ```python
            def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
                return row.get(name, row.get(name.upper(), default))
            ```


## Source link

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L978-L1080">View record_table_governance on GitHub</a>

```python
def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    *,
    spark_session: Any,
    context_reviews: list[dict[str, Any]] | None = None,
    dq_rule_reviews: list[dict[str, Any]] | None = None,
    classification_reviews: list[dict[str, Any]] | None = None,
    approved_by: str | None = None,
    governance_selection: dict[str, Any] | None = None,
    write_governance_review: bool = False,
    mode: str = "append",
) -> dict[str, Any]:
    """Persist approved table-governance review evidence.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration that routes metadata writes to
        the configured metadata lakehouse target.
    env : str
        Environment key in ``config``.
    profile_rows : list of dict
        Column-profile rows loaded for the selected catalogue table.
    spark_session : pyspark.sql.SparkSession
        Spark session used to create DataFrames for metadata writes.
    context_reviews, dq_rule_reviews, classification_reviews : list of dict, optional
        Human-approved rows from the governance review workflow. Only rows with
        ``review_status="approved"`` and ``commit=True`` are written.
    approved_by : str, optional
        Reviewer identity to stamp on records. When omitted, runtime defaults
        are used.
    governance_selection : dict, optional
        Catalogue selection used to re-read persisted evidence and write a final
        governance outcome row.
    write_governance_review : bool, default=False
        Whether to append a ``METADATA_GOVERNANCE_REVIEWS`` outcome row after
        checking agreement, pipeline, schema/profile, and DQ evidence.
    mode : str, default "append"
        Write mode for metadata table commits.

    Returns
    -------
    dict[str, Any]
        Records written for ``column_context``, ``dq_rules``, and
        ``column_classification`` plus an optional ``governance_review`` outcome.

    Notes
    -----
    This is the v1 governance commit action for ``03_governance`` notebooks. It merges
    the previous row-builder and per-table commit helpers into one explicit
    human approval step while preserving configured metadata lakehouse routing.
    """
    context_records = _build_column_context_records(
        profile_rows,
        context_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    dq_rule_records = _build_dq_rule_records(
        profile_rows,
        dq_rule_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    classification_records = _build_classification_records(
        profile_rows,
        classification_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    writes = {
        COLUMN_CONTEXT_TABLE: context_records,
        DQ_RULES_TABLE: dq_rule_records,
        COLUMN_CLASSIFICATION_TABLE: classification_records,
    }
    for table_name, records in writes.items():
        if records:
            write_lakehouse_table(spark_session.createDataFrame(records), config, env, "metadata", table_name, mode=mode)

    governance_review = None
    if write_governance_review:
        if governance_selection is None:
            raise ValueError("governance_selection is required when write_governance_review=True.")
        governance_review = _review_governance_evidence(
            config,
            env,
            governance_selection,
            spark_session=spark_session,
            reviewed_by=approved_by,
            mode=mode,
        )

    return {
        "column_context": context_records,
        "dq_rules": dq_rule_records,
        "column_classification": classification_records,
        "governance_review": governance_review,
    }
```

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.record_table_governance`
- Short name: `record_table_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `978`
- Inbound references count: 0
- Outbound references count: 5
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, metadata lakehouse, guardrail

### AI implementation contract

- **required_context:** Requires 03_governance profile rows and 00_env_config metadata routing; governance metadata must be written to the configured metadata target.
- **inputs:** config, env, profile_rows, spark_session, optional approved context/DQ/classification review rows, approved_by, and mode.
- **output:** Dictionary of records written for column_context, dq_rules, and column_classification.
- **side_effects:** Writes approved governance metadata records to configured metadata tables.
- **failure_modes:** Raises configuration, validation, Spark, or metadata-write errors when approved records cannot be built or persisted.
- **verification:** Verify review_status is approved and commit is true for intended rows before calling; confirm returned record groups match expected approvals.

### Inbound references

Not documented yet

### Outbound references

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- `fabricops_kit.governance_review._build_classification_records`
- `fabricops_kit.governance_review._build_column_context_records`
- `fabricops_kit.governance_review._build_dq_rule_records`
- `fabricops_kit.governance_review._review_governance_evidence`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L978-L1080">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/governance_review.py#L978-L1080</a>
- Start line: `978`
- End line: `1080`
- Signature:

```python
def record_table_governance(config: Any, env: str, profile_rows: list[dict[str, Any]], *, spark_session: Any, context_reviews: list[dict[str, Any]] | None=None, dq_rule_reviews: list[dict[str, Any]] | None=None, classification_reviews: list[dict[str, Any]] | None=None, approved_by: str | None=None, governance_selection: dict[str, Any] | None=None, write_governance_review: bool=False, mode: str='append') -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation summary

- Internal helper count: 29
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
