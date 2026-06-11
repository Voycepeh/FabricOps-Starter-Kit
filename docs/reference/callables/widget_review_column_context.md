# widget_review_column_context

Render standalone business-context review guidance for selected profile rows.

## What this is for and when to use it

Render standalone business-context review guidance for selected profile rows.

- Render standalone business-context review guidance for selected profile rows.

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
      <td data-label="Meaning">Selected column profile evidence from ``load_catalogue_profile_rows``.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

list[dict[str, Any]]
    Empty editable review list. Add approved context rows before calling
    ``record_table_governance``.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

Not documented yet

<details class="reference-implementation-details">
<summary>Implementation details</summary>

### Call flow

```text
widget_review_column_context(...)
└── _display_review_guidance(...)
    └── _value(...)
```

### Internal helpers used by this callable

### `def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/governance_review.py#L534-L548">View `_display_review_guidance` on GitHub</a>

**Code:**

```python
def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]:
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = [str(_value(row, "column_name")) for row in profile_rows]
    html = widgets.HTML(
        f"<h3>{title}</h3>"
        f"<p>{instructions}</p>"
        f"<p><b>Columns loaded:</b> {', '.join(columns)}</p>"
        "<p>Return value is an editable list scaffold. Add reviewed dictionaries, set "
        "<code>review_status='approved'</code> and <code>commit=True</code>, then pass the list to "
        "<code>record_table_governance</code>.</p>"
    )
    ip.display(html)
    return []
```

**Used here because:**

`widget_review_column_context` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_review_column_context` or another caller that reaches `_display_review_guidance`.

### `def _value(row: dict[str, Any], name: str, default: Any='') -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/governance_review.py#L70-L71">View `_value` on GitHub</a>

**Code:**

```python
def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))
```

**Used here because:**

`widget_review_column_context` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_review_column_context` or another caller that reaches `_value`.


</details>

## Source

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/governance_review.py#L551-L569">View widget_review_column_context on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def widget_review_column_context(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone business-context review guidance for ``03_governance``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved context rows before calling
        ``record_table_governance``.
    """
    return _display_review_guidance(
        "Business context review",
        profile_rows,
        "Describe human-approved business meaning for each column. AI suggestions, if used, are advisory only.",
    )
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_column_context`
- Short name: `widget_review_column_context`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `551`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected column profile evidence from ``load_catalogue_profile_rows``.
- **output:** list[dict[str, Any]]
    Empty editable review list. Add approved context rows before calling
    ``record_table_governance``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._display_review_guidance`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/governance_review.py#L551-L569">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/governance_review.py#L551-L569</a>
- Start line: `551`
- End line: `569`
- Signature:

```python
def widget_review_column_context(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation helpers

### Call flow

```text
widget_review_column_context(...)
└── _display_review_guidance(...)
    └── _value(...)
```

### Internal helpers used by this callable

### `def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/governance_review.py#L534-L548">View `_display_review_guidance` on GitHub</a>

**Code:**

```python
def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]:
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = [str(_value(row, "column_name")) for row in profile_rows]
    html = widgets.HTML(
        f"<h3>{title}</h3>"
        f"<p>{instructions}</p>"
        f"<p><b>Columns loaded:</b> {', '.join(columns)}</p>"
        "<p>Return value is an editable list scaffold. Add reviewed dictionaries, set "
        "<code>review_status='approved'</code> and <code>commit=True</code>, then pass the list to "
        "<code>record_table_governance</code>.</p>"
    )
    ip.display(html)
    return []
```

**Used here because:**

`widget_review_column_context` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_review_column_context` or another caller that reaches `_display_review_guidance`.

### `def _value(row: dict[str, Any], name: str, default: Any='') -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/governance_review.py#L70-L71">View `_value` on GitHub</a>

**Code:**

```python
def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))
```

**Used here because:**

`widget_review_column_context` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_review_column_context` or another caller that reaches `_value`.


</details>
