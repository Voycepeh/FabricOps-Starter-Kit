# widget_review_column_classification

## Purpose

Render standalone sensitivity and PII classification review guidance for selected profile rows.

## At a glance

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Item</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Item">Use when</td>
      <td data-label="Details">Render standalone sensitivity and PII classification review guidance for selected profile rows.</td>
    </tr>
    <tr>
      <td data-label="Item">Do not use when</td>
      <td data-label="Details">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Item">Example</td>
      <td data-label="Details">```python
Not documented yet
```</td>
    </tr>
    <tr>
      <td data-label="Item">Errors</td>
      <td data-label="Details">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Item">Side effects</td>
      <td data-label="Details">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Item">Related functions</td>
      <td data-label="Details">Not documented yet</td>
    </tr>
  </tbody>
</table>
</div>

## Parameters

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

## Returns

list[dict[str, Any]]
    Empty editable review list. Add approved classification dictionaries
    before calling ``record_table_governance``.

## Used by

No public or package-local callers detected by the generated dependency graph.

## Calls

- `fabricops_kit.governance_review._display_review_guidance`

## Implementation details

### Call flow

```text
widget_review_column_classification(...)
└── _display_review_guidance(...)
    └── _value(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L826-L844">View widget_review_column_classification on GitHub</a>

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

## Nested helper functions

??? info "Nested helper functions: 2"

    These helpers support `widget_review_column_classification` by handling shared implementation tasks reached from the public call flow; expand the source block only when you need maintainer-level details.

    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Helper</th>
          <th>Role</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Helper"><code>_display_review_guidance</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L534-L548"><code>src/fabricops_kit/governance_review.py#L534-L548</code></a></td>
        </tr>
        <tr>
          <td data-label="Helper"><code>_value</code></td>
          <td data-label="Role">Internal helper used by the package implementation.</td>
          <td data-label="Source"><a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L70-L71"><code>src/fabricops_kit/governance_review.py#L70-L71</code></a></td>
        </tr>
      </tbody>
    </table>

    ??? example "View helper source code"

        **`def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]`**

        Used by `widget_review_column_classification` through the implementation path shown above.

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

        Used by `widget_review_column_classification` through the implementation path shown above.

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
- Source line: `826`
- Inbound references count: 0
- Outbound references count: 1

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L826-L844">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L826-L844</a>
- Start line: `826`
- End line: `844`
- Signature:

```python
def widget_review_column_classification(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

### Internal relationship graph

The human-readable implementation view above is the source of truth for public call flow, public callable source, and collapsed nested helper details.

### Public related functions

Not documented yet

### Call flow

```text
widget_review_column_classification(...)
└── _display_review_guidance(...)
    └── _value(...)
```

</details>
