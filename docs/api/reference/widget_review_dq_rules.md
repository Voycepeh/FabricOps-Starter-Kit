# widget_review_dq_rules

Render standalone DQ-rule review guidance for selected profile rows.

## Purpose

This API reference documents the callable summarized above. Use the sections below for when to use it, inputs, return values, template usage, and implementation details.

## When to use this

- Render standalone DQ-rule review guidance for selected profile rows.

## At a glance

**Do not use when:**

- Not documented yet

**Errors:**

Not documented yet

**Side effects:**

Not documented yet

## Used in templates

- `03_governance`

## Used by

Not documented yet

## Calls

- `fabricops_kit.governance_review._canonical_dq_rule_type`
- `fabricops_kit.governance_review._dq_parameter_fields_for_rule_type`
- `fabricops_kit.governance_review._dq_rule_display_rows`
- `fabricops_kit.governance_review._draft_dq_rules`
- `fabricops_kit.governance_review._validate_dq_rules`
- `fabricops_kit.governance_review._value`

## Function details and source

### Function details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `624`
- Signature:

```python
def widget_review_dq_rules(profile_rows: list[dict[str, Any]], *, existing_rules: list[dict[str, Any]] | None=None, config: Any=None, env: str | None=None, spark_session: Any=None, table_name: str | None=None, business_context: str='') -> list[dict[str, Any]]
```

### Parameters

`profile_rows` : `list[dict[str, Any]]`, required
: Selected catalogue profile rows containing columns and profile evidence.

`existing_rules` : `list[dict[str, Any]] | None`, optional
: Previously persisted active and inactive DQ rule rows for the selected table. When supplied, the widget displays them in an editable review table. Runtime enforcement still reads ``METADATA_DQ_RULES`` later.

`config` : `Any`, optional
: Runtime objects used only when reviewers click AI suggestion actions.

`env` : `str | None`, optional
: Not documented yet

`spark_session` : `Any`, optional
: Not documented yet

`table_name` : `str | None`, optional
: Selected table name. Defaults to the table in ``profile_rows``.

`business_context` : `str`, optional
: Optional context sent to the Fabric AI suggestion helper.

### Returns

list[dict[str, Any]]
    Mutable review list. The widget appends approved create, update,
    deactivation, and reactivation dictionaries to this list; pass it to
    ``record_table_governance`` to persist append-only metadata history.

### Return interpretation

Interpret the returned value according to the Returns section above.

### Common failure causes

No common failure causes are documented beyond the Errors section.

### Notes

No additional callable notes are documented.

### Example

```python
Not documented yet
```

### Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L624-L787">View widget_review_dq_rules on GitHub</a>

```python
def widget_review_dq_rules(
    profile_rows: list[dict[str, Any]],
    *,
    existing_rules: list[dict[str, Any]] | None = None,
    config: Any = None,
    env: str | None = None,
    spark_session: Any = None,
    table_name: str | None = None,
    business_context: str = "",
) -> list[dict[str, Any]]:
    """Render a table-driven DQ-rule review widget for ``03_governance``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected catalogue profile rows containing columns and profile evidence.
    existing_rules : list of dict, optional
        Previously persisted active and inactive DQ rule rows for the selected
        table. When supplied, the widget displays them in an editable review
        table. Runtime enforcement still reads ``METADATA_DQ_RULES`` later.
    config, env, spark_session : optional
        Runtime objects used only when reviewers click AI suggestion actions.
    table_name : str, optional
        Selected table name. Defaults to the table in ``profile_rows``.
    business_context : str, default=""
        Optional context sent to the Fabric AI suggestion helper.

    Returns
    -------
    list[dict[str, Any]]
        Mutable review list. The widget appends approved create, update,
        deactivation, and reactivation dictionaries to this list; pass it to
        ``record_table_governance`` to persist append-only metadata history.
    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    review_rows: list[dict[str, Any]] = []
    columns = [str(_value(row, "column_name")) for row in profile_rows]
    selected_table = table_name or str(_value(profile_rows[0], "table_name") if profile_rows else "")
    rules_table = _dq_rule_display_rows(existing_rules or [])

    table_dropdown = widgets.Dropdown(options=[selected_table] if selected_table else [], value=selected_table or None, description="Table")
    rule_type_dropdown = widgets.Dropdown(options=DQ_RULE_TYPES, value="not_null", description="Rule")
    column_select = widgets.SelectMultiple(options=columns, description="Columns", rows=min(max(len(columns), 4), 12), layout=widgets.Layout(width="420px"))
    severity = widgets.ToggleButtons(options=["warning", "error"], value="warning", description="Severity")
    description = widgets.Textarea(description="Description", layout=widgets.Layout(width="760px", height="70px"))
    params = widgets.Textarea(description="Parameters JSON", value="{}", layout=widgets.Layout(width="760px", height="90px"))
    parameter_guidance = widgets.HTML()
    rule_id = widgets.Text(description="Rule ID", layout=widgets.Layout(width="760px"))
    preview = widgets.Textarea(description="Preview", disabled=True, layout=widgets.Layout(width="900px", height="160px"))
    existing_options = [(f"{r['Rule ID']} · {r['Rule type']} · {r['Column(s)']} · {r['Status']}", i) for i, r in enumerate(rules_table)]
    existing_select = widgets.Dropdown(options=existing_options, description="Edit rule") if existing_options else widgets.HTML("<i>No existing rules supplied for this table.</i>")
    rules_html = widgets.HTML("<pre>" + json.dumps(rules_table, indent=2, default=str) + "</pre>")
    message = widgets.HTML()

    def current_rule(action_type: str = "created") -> dict[str, Any]:
        extra = json.loads(params.value or "{}")
        cols = list(column_select.value)
        draft = {
            "rule_id": rule_id.value or f"{selected_table}_{rule_type_dropdown.value}_{uuid.uuid4().hex[:8]}",
            "rule_type": rule_type_dropdown.value,
            "columns": cols,
            "severity": severity.value,
            "description": description.value,
            "is_active": action_type != "deactivated",
            "review_status": "approved",
            "action_type": action_type,
            "commit": True,
            **extra,
        }
        _validate_dq_rules([draft])
        return draft

    def refresh_parameter_guidance(*_: Any) -> None:
        required = _dq_parameter_fields_for_rule_type(rule_type_dropdown.value)
        if required:
            parameter_guidance.value = f"<b>Required parameters for this rule:</b> {', '.join(required)}"
        else:
            parameter_guidance.value = "<b>No extra parameters required.</b>"

    def refresh_preview(*_: Any) -> None:
        refresh_parameter_guidance()
        try:
            preview.value = json.dumps(current_rule("created"), indent=2, default=str)
            message.value = ""
        except Exception as exc:
            preview.value = ""
            message.value = f"<b>Validation:</b> {exc}"

    def load_existing(_: Any = None) -> None:
        if not existing_options or not hasattr(existing_select, "value"):
            return
        source = (existing_rules or [])[int(existing_select.value)]
        raw = source.get("rule_parameters_json") or "{}"
        try:
            parsed = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except Exception:
            parsed = {}
        cols = parsed.pop("columns", None) or source.get("columns") or source.get("column_name") or []
        if isinstance(cols, str):
            cols = [c.strip() for c in cols.split(",") if c.strip()]
        rule_id.value = str(source.get("rule_id") or "")
        rule_type_dropdown.value = _canonical_dq_rule_type(source.get("rule_type"))
        column_select.value = tuple(c for c in cols if c in columns)
        severity.value = str(source.get("severity") or "warning")
        description.value = str(source.get("description") or "")
        params.value = json.dumps(parsed, indent=2, default=str)
        refresh_preview()

    def append_action(action: str) -> None:
        try:
            review_rows.append(current_rule(action))
            message.value = f"<b>Queued {action}.</b> Pass the returned list to record_table_governance to commit."
        except Exception as exc:
            message.value = f"<b>Cannot queue action:</b> {exc}"

    def suggest_ai(_: Any = None) -> None:
        try:
            prompt = getattr(getattr(config, "ai_prompt_config", None), "dq_rule_suggestion_prompt_template", "") if config is not None else ""
            profile_df = spark_session.createDataFrame(profile_rows) if spark_session is not None and not hasattr(profile_rows, "ai") else profile_rows
            drafts = _draft_dq_rules(profile_df=profile_df, table_name=selected_table, business_context=business_context, prompt_template=prompt, config=config)
            for draft in drafts:
                draft.update({"review_status": "draft", "is_active": False, "commit": False})
            review_rows.extend(drafts)
            message.value = f"<b>Loaded {len(drafts)} AI draft suggestion(s).</b> Review, edit, and mark commit=True before approval."
        except Exception as exc:
            message.value = f"<b>AI suggestion failed:</b> {exc}"

    for control in (rule_type_dropdown, column_select, severity, description, params, rule_id):
        control.observe(lambda change: refresh_preview(), names="value")
    if hasattr(existing_select, "observe"):
        existing_select.observe(lambda change: load_existing(), names="value")

    create_button = widgets.Button(description="Save approved active rule", button_style="success")
    update_button = widgets.Button(description="Update selected rule", button_style="info")
    delete_button = widgets.Button(description="Delete / deactivate", button_style="warning")
    reactivate_button = widgets.Button(description="Reactivate", button_style="success")
    ai_button = widgets.Button(description="AI suggest rules", button_style="")
    create_button.on_click(lambda _: append_action("created"))
    update_button.on_click(lambda _: append_action("updated"))
    delete_button.on_click(lambda _: append_action("deactivated"))
    reactivate_button.on_click(lambda _: append_action("reactivated"))
    ai_button.on_click(suggest_ai)

    refresh_preview()
    ip.display(widgets.VBox([
        widgets.HTML("<h3>DQ rule review</h3><p>Select a table, review columns and existing active/inactive rules, then queue append-only create/update/deactivate/reactivate actions.</p>"),
        table_dropdown,
        widgets.HTML(f"<b>Columns in selected table:</b> {', '.join(columns)}"),
        widgets.HTML("<h4>Existing rules for selected table</h4>"),
        rules_html,
        existing_select,
        widgets.HBox([rule_type_dropdown, column_select]),
        rule_id,
        parameter_guidance,
        params,
        severity,
        description,
        preview,
        widgets.HBox([create_button, update_button, delete_button, reactivate_button, ai_button]),
        message,
    ]))
    return review_rows
```

## Internal implementation summary

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in the internal implementation summary.

    ```text
    widget_review_dq_rules(...)
    ├── _canonical_dq_rule_type(...)
    ├── _dq_parameter_fields_for_rule_type(...)
    │   └── _canonical_dq_rule_type(...)
    ├── _dq_rule_display_rows(...)
    │   ├── _canonical_dq_rule_type(...)
    │   └── _dq_rule_parameters_summary(...)
    ├── _draft_dq_rules(...)
    │   ├── _canonical_dq_rule_type(...)
    │   ├── _extract_assignment_payload(...)
    │   │   └── …
    │   ├── _prepare_dq_profile_input_rows(...)
    │   │   └── …
    │   ├── _run_fabric_ai_drafting(...)
    │   └── _validate_dq_rules(...)
    │       └── …
    ├── _validate_dq_rules(...)
    │   └── _canonical_dq_rule_type(...)
    └── _value(...)
    ```

??? info "Internal helpers used: 16"

    This callable uses 16 internal helpers for audit timestamp, metadata loading, rule parsing, rule evaluation, fabric or spark access, and other.

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
          <td data-label="Helpers"><code>_dq_rule_display_rows</code>, <code>_draft_dq_rules</code>, <code>_extract_assignment_payload</code>, <code>_validate_dq_rules</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_canonical_dq_rule_type</code>, <code>_dq_parameter_fields_for_rule_type</code>, <code>_parse_ai_dict_response</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule evaluation</td>
          <td data-label="Helpers"><code>_dq_rule_parameters_summary</code>, <code>_prepare_dq_profile_input_rows</code>, <code>_spark_sql_helpers</code></td>
          <td data-label="What they do">Convert configured rules into executable checks and evaluation results.</td>
        </tr>
        <tr>
          <td data-label="Area">Fabric or Spark access</td>
          <td data-label="Helpers"><code>_run_fabric_ai_drafting</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_coerce_rows</code>, <code>_value</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L69-L75)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L61-L66)

            ```python
            def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
                """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
                if timezone_name is not None:
                    return _validate_audit_timezone(timezone_name)
                value = getattr(config, "audit_timezone", None) if config is not None else None
                return _validate_audit_timezone(value)
            ```

            **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L27-L58)

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

            **`def _dq_rule_display_rows(rules: list[dict[str, Any]]) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L553-L583)

            ```python
            def _dq_rule_display_rows(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
                """Return table-shaped rows for active and inactive selected-table rules."""
                rows = []
                for rule in rules or []:
                    params = rule.get("rule_parameters") or {}
                    raw = rule.get("rule_parameters_json")
                    if raw and not params:
                        try:
                            params = json.loads(raw) if isinstance(raw, str) else {}
                        except Exception:
                            params = {}
                    cols = params.get("columns") or rule.get("columns") or rule.get("column_name") or ""
                    if isinstance(cols, list):
                        cols_display = ", ".join(str(c) for c in cols)
                    else:
                        cols_display = str(cols)
                    rows.append({
                        "Rule ID": str(rule.get("rule_id") or ""),
                        "Rule type": _canonical_dq_rule_type(rule.get("rule_type")),
                        "Column(s)": cols_display,
                        "Parameters summary": _dq_rule_parameters_summary(rule),
                        "Severity": str(rule.get("severity") or "warning"),
                        "Status": "active" if bool(rule.get("is_active", True)) else "inactive",
                        "Review status": str(rule.get("review_status") or ""),
                        "Approved by": str(rule.get("approved_by") or ""),
                        "Approved at": str(rule.get("approved_at") or ""),
                        "Last action": str(rule.get("action_type") or ""),
                        "Committed at": str(rule.get("_committed_at") or ""),
                        "Description": str(rule.get("description") or ""),
                    })
                return rows
            ```

            **`def _draft_dq_rules(*, profile_df=None, df=None, table_name: str, business_context: str='', prompt_template: str | None=None, output_col: str='response', config: Any=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L1585-L1593)

            ```python
            def _draft_dq_rules(*, profile_df=None, df=None, table_name: str, business_context: str = "", prompt_template: str | None = None, output_col: str = "response", config: Any = None) -> list[dict[str, Any]]:
                """Draft candidate DQ rules from metadata profiles or a raw DataFrame fallback."""
                prepared = _prepare_dq_profile_input_rows(profile_df=profile_df, df=df, table_name=table_name, business_context=business_context, config=config)
                responses = _run_fabric_ai_drafting(prepared, prompt=prompt_template or DQ_RULE_SUGGESTION_PROMPT, output_col=output_col)
                candidates = _extract_assignment_payload(responses, response_col=output_col, assignment_key="DQ_RULES", table_name=table_name)
                by_id = {r.get("rule_id"): {**r, "rule_type": _canonical_dq_rule_type(r.get("rule_type"))} for r in candidates if r.get("rule_id")}
                rules = list(by_id.values())
                _validate_dq_rules(rules)
                return rules
            ```

            **`def _extract_assignment_payload(response_rows, *, response_col: str, assignment_key: str | None=None, table_name: str | None=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L1129-L1143)

            ```python
            def _extract_assignment_payload(response_rows, *, response_col: str, assignment_key: str | None = None, table_name: str | None = None) -> list[dict[str, Any]]:
                """Extract dictionary payloads from AI response rows with optional table-key narrowing."""
                out: list[dict[str, Any]] = []
                for row in _coerce_rows(response_rows):
                    parsed = _parse_ai_dict_response(row.get(response_col) or row.get("response") or row.get("ai_response") or "")
                    if not parsed:
                        continue
                    payload = parsed.get(assignment_key, parsed) if assignment_key else parsed
                    if table_name is not None:
                        payload = payload.get(table_name, []) if isinstance(payload, dict) else []
                    if isinstance(payload, list):
                        out.extend(dict(item) for item in payload if isinstance(item, dict))
                    elif isinstance(payload, dict):
                        out.append(payload)
                return out
            ```

            **`def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L1146-L1219)

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

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L78-L79)

            ```python
            def _canonical_dq_rule_type(rule_type: Any) -> str:
                return str(rule_type or "").strip()
            ```

            **`def _dq_parameter_fields_for_rule_type(rule_type: str) -> list[str]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L586-L604)

            ```python
            def _dq_parameter_fields_for_rule_type(rule_type: str) -> list[str]:
                """Return parameter names a reviewer should fill for a rule type."""
                return {
                    "null_rate_below": ["max_null_percent"],
                    "accepted_values": ["allowed_values"],
                    "not_in_values": ["blocked_values"],
                    "between": ["min_value", "max_value"],
                    "date_between": ["min_value", "max_value"],
                    "greater_than": ["value"],
                    "greater_than_or_equal": ["value"],
                    "less_than": ["value"],
                    "less_than_or_equal": ["value"],
                    "regex_match": ["regex_pattern"],
                    "freshness": ["max_age_days"],
                    "max_age_days": ["max_age_days"],
                    "required_when": ["condition"],
                    "value_when": ["condition", "expected_value"],
                    "expression_true": ["expression"],
                }.get(_canonical_dq_rule_type(rule_type), [])
            ```

            **`def _parse_ai_dict_response(text: str) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L1111-L1126)

            ```python
            def _parse_ai_dict_response(text: str) -> dict[str, Any]:
                """Parse JSON/Python-dict AI response text into a dictionary."""
                cleaned = str(text or "").strip()
                match = re.search(r"^[A-Z_]+\s*=\s*(\{.*\})\s*$", cleaned, flags=re.DOTALL)
                if match:
                    cleaned = match.group(1)
                if not cleaned:
                    return {}
                for loader in (json.loads, ast.literal_eval):
                    try:
                        obj = loader(cleaned)
                    except Exception:
                        continue
                    if isinstance(obj, dict):
                        return obj
                return {}
            ```

        ??? example "Rule evaluation helpers"

            **`def _dq_rule_parameters_summary(rule: dict[str, Any]) -> str`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L535-L550)

            ```python
            def _dq_rule_parameters_summary(rule: dict[str, Any]) -> str:
                """Return compact display text for non-identity DQ parameters."""
                params = dict(rule.get("rule_parameters") or {})
                raw = rule.get("rule_parameters_json")
                if raw and not params:
                    try:
                        params = json.loads(raw) if isinstance(raw, str) else dict(raw)
                    except Exception:
                        params = {}
                if not params:
                    params = {k: v for k, v in rule.items() if k in {
                        "max_null_percent", "allowed_values", "blocked_values", "min_value", "max_value", "value",
                        "regex_pattern", "max_age_days", "condition", "expected_value", "expression",
                    }}
                params.pop("columns", None)
                return ", ".join(f"{k}={v}" for k, v in sorted(params.items()))
            ```

            **`def _prepare_dq_profile_input_rows(*, profile_df=None, df=None, table_name: str, business_context: str='', config: Any=None)`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L1558-L1582)

            ```python
            def _prepare_dq_profile_input_rows(*, profile_df=None, df=None, table_name: str, business_context: str = "", config: Any = None):
                """Prepare DQ prompt profile rows from a profile DataFrame or raw DataFrame."""
                if (profile_df is None) == (df is None):
                    raise ValueError("Provide exactly one of profile_df or df.")
                if profile_df is None:
                    profile_df = profile_dataframe(df, table_name=table_name, config=config)
                cols = set(profile_df.columns)
                if {"column_name", "data_type", "row_count", "null_count", "distinct_count"}.issubset(cols):
                    return profile_df
                _, F, _ = _spark_sql_helpers()
                return profile_df.select(
                    F.col("TABLE_NAME").alias("table_name"),
                    F.col("COLUMN_NAME").alias("column_name"),
                    F.col("DATA_TYPE").alias("data_type"),
                    F.col("ROW_COUNT").alias("row_count"),
                    F.col("NULL_COUNT").alias("null_count"),
                    F.col("NULL_PERCENT").alias("null_percent"),
                    F.col("DISTINCT_COUNT").alias("distinct_count"),
                    F.col("DISTINCT_PERCENT").alias("distinct_percent"),
                    F.col("MIN_VALUE").alias("min_value"),
                    F.col("MAX_VALUE").alias("max_value"),
                    F.lit("").alias("observed_values_sample"),
                    F.lit(business_context).alias("business_context"),
                    F.lit(_current_audit_timestamp(config=config, drop_microseconds=False)).alias("profile_timestamp"),
                )
            ```

            **`def _spark_sql_helpers()`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L1083-L1090)

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

        ??? example "Fabric or Spark access helpers"

            **`def _run_fabric_ai_drafting(prepared_profile_df, *, prompt: str, output_col: str)`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L1093-L1098)

            ```python
            def _run_fabric_ai_drafting(prepared_profile_df, *, prompt: str, output_col: str):
                """Run Fabric AI prompt drafting against prepared profile rows."""
                ai = getattr(prepared_profile_df, "ai", None)
                if ai is None or not hasattr(ai, "generate_response"):
                    raise RuntimeError("AI drafting requires Fabric DataFrame.ai.generate_response.")
                return prepared_profile_df.ai.generate_response(prompt=prompt, is_prompt_template=True, output_col=output_col)
            ```

        ??? example "Other helpers"

            **`def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L62-L67)

            ```python
            def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
                if rows_or_df is None:
                    return []
                if hasattr(rows_or_df, "collect"):
                    rows_or_df = rows_or_df.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
            ```

            **`def _value(row: dict[str, Any], name: str, default: Any='') -> Any`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L70-L71)

            ```python
            def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
                return row.get(name, row.get(name.upper(), default))
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_dq_rules`
- Short name: `widget_review_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `624`
- Inbound references count: 0
- Outbound references count: 6
- Used in templates: 03_governance
- Glossary terms: —

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected catalogue profile rows containing columns and profile evidence.
existing_rules : list of dict, optional
    Previously persisted active and inactive DQ rule rows for the selected
    table. When supplied, the widget displays them in an editable review
    table. Runtime enforcement still reads ``METADATA_DQ_RULES`` later.
config, env, spark_session : optional
    Runtime objects used only when reviewers click AI suggestion actions.
table_name : str, optional
    Selected table name. Defaults to the table in ``profile_rows``.
business_context : str, default=""
    Optional context sent to the Fabric AI suggestion helper.
- **output:** list[dict[str, Any]]
    Mutable review list. The widget appends approved create, update,
    deactivation, and reactivation dictionaries to this list; pass it to
    ``record_table_governance`` to persist append-only metadata history.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._canonical_dq_rule_type`
- `fabricops_kit.governance_review._dq_parameter_fields_for_rule_type`
- `fabricops_kit.governance_review._dq_rule_display_rows`
- `fabricops_kit.governance_review._draft_dq_rules`
- `fabricops_kit.governance_review._validate_dq_rules`
- `fabricops_kit.governance_review._value`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L624-L787">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L624-L787</a>
- Start line: `624`
- End line: `787`
- Signature:

```python
def widget_review_dq_rules(profile_rows: list[dict[str, Any]], *, existing_rules: list[dict[str, Any]] | None=None, config: Any=None, env: str | None=None, spark_session: Any=None, table_name: str | None=None, business_context: str='') -> list[dict[str, Any]]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 16
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
