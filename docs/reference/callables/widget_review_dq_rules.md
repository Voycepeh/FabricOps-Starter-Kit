# widget_review_dq_rules

Render standalone DQ-rule review guidance for selected profile rows.

## What this is for and when to use it

Render standalone DQ-rule review guidance for selected profile rows.

- Render standalone DQ-rule review guidance for selected profile rows.

## When not to use it

- Not documented yet

## Example

```python
Not documented yet
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
      <td data-label="Parameter"><code>profile_rows</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Selected catalogue profile rows containing columns and profile evidence.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>existing_rules</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Previously persisted active and inactive DQ rule rows for the selected table. When supplied, the widget displays them in an editable review table. Runtime enforcement still reads ``METADATA_DQ_RULES`` later.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Runtime objects used only when reviewers click AI suggestion actions.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Selected table name. Defaults to the table in ``profile_rows``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>business_context</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Optional context sent to the Fabric AI suggestion helper.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

list[dict[str, Any]]
    Mutable review list. The widget appends approved create, update,
    deactivation, and reactivation dictionaries to this list; pass it to
    ``record_table_governance`` to persist append-only metadata history.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

Not documented yet

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
- <a href="../internal/governance_review__dq_parameter_fields_for_rule_type/"><code>fabricops_kit.governance_review._dq_parameter_fields_for_rule_type</code></a>
- <a href="../internal/governance_review__dq_rule_display_rows/"><code>fabricops_kit.governance_review._dq_rule_display_rows</code></a>
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ffb9386812c13cf40a6a40503d36bd7a16dc5e31/src/fabricops_kit/governance_review.py#L662-L825">View widget_review_dq_rules on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

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
            drafts = _draft_dq_rules(profile_df=profile_df, table_name=selected_table, business_context=business_context, prompt_template=prompt)
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

</details>

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
- Source line: `662`
- Inbound references count: 0
- Outbound references count: 6

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

- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
- <a href="../internal/governance_review__dq_parameter_fields_for_rule_type/"><code>fabricops_kit.governance_review._dq_parameter_fields_for_rule_type</code></a>
- <a href="../internal/governance_review__dq_rule_display_rows/"><code>fabricops_kit.governance_review._dq_rule_display_rows</code></a>
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ffb9386812c13cf40a6a40503d36bd7a16dc5e31/src/fabricops_kit/governance_review.py#L662-L825">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ffb9386812c13cf40a6a40503d36bd7a16dc5e31/src/fabricops_kit/governance_review.py#L662-L825</a>
- Start line: `662`
- End line: `825`
- Signature:

```python
def widget_review_dq_rules(profile_rows: list[dict[str, Any]], *, existing_rules: list[dict[str, Any]] | None=None, config: Any=None, env: str | None=None, spark_session: Any=None, table_name: str | None=None, business_context: str='') -> list[dict[str, Any]]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation helpers

- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
- <a href="../internal/governance_review__dq_parameter_fields_for_rule_type/"><code>fabricops_kit.governance_review._dq_parameter_fields_for_rule_type</code></a>
- <a href="../internal/governance_review__dq_rule_display_rows/"><code>fabricops_kit.governance_review._dq_rule_display_rows</code></a>
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>

</details>
