# widget_review_column_context

Render standalone business-context review guidance for selected profile rows.

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance when profile rows need human-reviewed column descriptions or business meaning.

**Additional context:**

Renders review guidance for column business context so reviewers can approve or edit metadata for a selected table.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_review_column_context(
    profile_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
Not documented yet
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `profile_rows` | `list[dict[str, Any]]` | Yes | Selected column profile evidence from ``load_catalogue_profile_rows``. |

## Returns

list[dict[str, Any]]
    Empty editable review list. Add approved context rows before calling
    ``record_table_governance``.

### Return interpretation

The widget captures review state; approved rows must still be passed to record_table_governance to persist metadata.

## Raises / Errors

Not documented yet

### Common failure causes

- No profile rows are loaded.
- Required review fields are incomplete.
- Widget dependencies are unavailable.
- Reviewer changes are not committed before persistence.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.governance_review._display_review_guidance`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    widget_review_column_context(...)
    └── _display_review_guidance(...)
        └── _value(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L497-L511"><code>_display_review_guidance</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>
        </div>
      </section>
    </div>

    ??? example "View helper source by area"

        ??? example "Other helpers"

            **`def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L497-L511)

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

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L70-L71)

            ```python
            def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
                return row.get(name, row.get(name.upper(), default))
            ```


<div class="reference-source-card">
  <p><strong>Source:</strong> <code>fabricops_kit/governance_review.py:514</code></p>
  <p><strong>Actions:</strong> <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L514-L532">View on GitHub</a></p>
</div>

??? example "Source code"

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

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_column_context`
- Short name: `widget_review_column_context`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `514`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, notebook template

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L514-L532">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L514-L532</a>
- Start line: `514`
- End line: `532`
- Signature:

```python
def widget_review_column_context(
    profile_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary and optional source snippets are rendered in the page-level Implementation details section.

</details>

## Source link

- Source: `fabricops_kit/governance_review.py:514`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c4d665ddd08b8c281ac8a97f8e2ce0ba80ff0d05/src/fabricops_kit/governance_review.py#L514-L532">View widget_review_column_context on GitHub</a>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
