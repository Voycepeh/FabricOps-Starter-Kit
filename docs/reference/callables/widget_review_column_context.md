# widget_review_column_context

Render standalone business-context review guidance for selected profile rows.

## Purpose

Render standalone business-context review guidance for selected profile rows.

## At a glance

**Use when:**

- Render standalone business-context review guidance for selected profile rows.

**Do not use when:**

- Not documented yet

**Example:**

```python
Not documented yet
```

**Errors:**

Not documented yet

**Side effects:**

Not documented yet

## Used by

Not documented yet

## Calls

- `fabricops_kit.governance_review._display_review_guidance`

## Callable implementation

### Function details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `551`
- Signature:

```python
def widget_review_column_context(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
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
      <td data-label="Parameter"><code>profile_rows</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Selected column profile evidence from ``load_catalogue_profile_rows``.</td>
    </tr>
  </tbody>
</table>
</div>

### Returns

list[dict[str, Any]]
    Empty editable review list. Add approved context rows before calling
    ``record_table_governance``.

### Notes

No additional callable notes are documented.

### Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/2319e3488b66212cd694b16ac27f58b6909d12af/src/fabricops_kit/governance_review.py#L551-L569">View widget_review_column_context on GitHub</a>

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

## Internal implementation summary

??? info "Call flow"

    ```text
    widget_review_column_context(...)
    └── _display_review_guidance(...)
        └── _value(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for other.

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
          <td data-label="Helpers"><code>_display_review_guidance</code>, <code>_value</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Other helpers"

            **`def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/2319e3488b66212cd694b16ac27f58b6909d12af/src/fabricops_kit/governance_review.py#L534-L548)

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

            **`def _value(row: dict[str, Any], name: str, default: Any='') -> Any`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/2319e3488b66212cd694b16ac27f58b6909d12af/src/fabricops_kit/governance_review.py#L70-L71)

            ```python
            def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
                return row.get(name, row.get(name.upper(), default))
            ```


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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/2319e3488b66212cd694b16ac27f58b6909d12af/src/fabricops_kit/governance_review.py#L551-L569">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/2319e3488b66212cd694b16ac27f58b6909d12af/src/fabricops_kit/governance_review.py#L551-L569</a>
- Start line: `551`
- End line: `569`
- Signature:

```python
def widget_review_column_context(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
