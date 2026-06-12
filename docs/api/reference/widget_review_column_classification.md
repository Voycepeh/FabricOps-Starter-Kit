# widget_review_column_classification

Render standalone sensitivity and PII classification review guidance for selected profile rows.

## Purpose

Renders sensitivity and PII classification review guidance for columns in a selected table.

## When to use this

- Use in 03_governance when reviewers need to approve classification metadata before governance records are written.

## At a glance

**Do not use when:**

- Not documented yet

**Errors:**

Not documented yet

**Side effects:**

Not documented yet

## Key terms

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../reference/glossary/) for more FabricOps terms.

## Related guides

- [Governance Review](../../how-fabricops-works/governance-review.md)

## Used in templates

- `03_governance`

## Used by

Not documented yet

## Calls

- `fabricops_kit.governance_review._display_review_guidance`

## Function details and source

### Function details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `789`
- Signature:

```python
def widget_review_column_classification(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

### Parameters

`profile_rows` : `list[dict[str, Any]]`, required
: Selected column profile evidence from ``load_catalogue_profile_rows``.

### Returns

list[dict[str, Any]]
    Empty editable review list. Add approved classification dictionaries
    before calling ``record_table_governance``.

### Return interpretation

The widget captures classification review state; approved classifications must be included in record_table_governance to persist them.

### Common failure causes

- No selected profile rows are available.
- Classification choices are incomplete.
- Reviewer approval status is missing.
- Widget state is not collected before persistence.

### Notes

No additional callable notes are documented.

### Example

```python
Not documented yet
```

### Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L789-L807">View widget_review_column_classification on GitHub</a>

```python
def widget_review_column_classification(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone sensitivity and PII classification review guidance.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved classification dictionaries
        before calling ``record_table_governance``.
    """
    return _display_review_guidance(
        "Sensitivity and PII classification review",
        profile_rows,
        "Review sensitivity labels, personal-data classifications, identifier types, and handling requirements.",
    )
```

## Internal implementation summary

??? info "Call flow"

    ```text
    widget_review_column_classification(...)
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

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L497-L511)

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

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L70-L71)

            ```python
            def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
                return row.get(name, row.get(name.upper(), default))
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_column_classification`
- Short name: `widget_review_column_classification`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `789`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** profile_rows : list of dict
    Selected column profile evidence from ``load_catalogue_profile_rows``.
- **output:** list[dict[str, Any]]
    Empty editable review list. Add approved classification dictionaries
    before calling ``record_table_governance``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._display_review_guidance`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L789-L807">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L789-L807</a>
- Start line: `789`
- End line: `807`
- Signature:

```python
def widget_review_column_classification(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
