# get_selected_catalogue_table

Return the table selected by widget_select_catalogue_table.

## Purpose

Return the table selected by widget_select_catalogue_table.

## At a glance

**Use when:**

- Return the table selected by widget_select_catalogue_table.

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

Not documented yet

## Function details and source

### Function details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `310`
- Signature:

```python
def get_selected_catalogue_table(table_selector: Any | None=None) -> dict[str, Any]
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
      <td data-label="Parameter"><code>table_selector</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Selector returned by ``widget_select_catalogue_table``. Passing it is optional because the widget also maintains module-level selection state.</td>
    </tr>
  </tbody>
</table>
</div>

### Returns

dict[str, Any]
    Stable table identity used by ``load_catalogue_profile_rows``.

### Notes

No additional callable notes are documented.

### Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acbcda756eb6c5d0ac4280cc006bfabd6f41c579/src/fabricops_kit/governance_review.py#L310-L334">View get_selected_catalogue_table on GitHub</a>

```python
def get_selected_catalogue_table(table_selector: Any | None = None) -> dict[str, Any]:
    """Return the catalogue table selected by ``widget_select_catalogue_table``.

    Parameters
    ----------
    table_selector : ipywidgets.Combobox, optional
        Selector returned by ``widget_select_catalogue_table``. Passing it is
        optional because the widget also maintains module-level selection state.

    Returns
    -------
    dict[str, Any]
        Stable table identity used by ``load_catalogue_profile_rows``.
    """
    if _SELECTED_CATALOGUE_TABLE is not None:
        return dict(_SELECTED_CATALOGUE_TABLE)
    raw_value = getattr(table_selector, "value", None) if table_selector is not None else None
    if raw_value:
        try:
            parsed = json.loads(str(raw_value))
            if isinstance(parsed, dict):
                return dict(parsed)
        except json.JSONDecodeError:
            pass
    raise ValueError("No catalogue table has been selected. Run widget_select_catalogue_table first.")
```

## Internal implementation summary

??? info "Call flow"

    ```text
    get_selected_catalogue_table(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `get_selected_catalogue_table` does not have package-local helper descendants in the generated call graph.

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
          <td data-label="Area">—</td>
          <td data-label="Helpers">—</td>
          <td data-label="What they do">No internal helpers detected.</td>
        </tr>
      </tbody>
    </table>
    </div>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.get_selected_catalogue_table`
- Short name: `get_selected_catalogue_table`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `310`
- Inbound references count: 0
- Outbound references count: 0

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** table_selector : ipywidgets.Combobox, optional
    Selector returned by ``widget_select_catalogue_table``. Passing it is
    optional because the widget also maintains module-level selection state.
- **output:** dict[str, Any]
    Stable table identity used by ``load_catalogue_profile_rows``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acbcda756eb6c5d0ac4280cc006bfabd6f41c579/src/fabricops_kit/governance_review.py#L310-L334">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acbcda756eb6c5d0ac4280cc006bfabd6f41c579/src/fabricops_kit/governance_review.py#L310-L334</a>
- Start line: `310`
- End line: `334`
- Signature:

```python
def get_selected_catalogue_table(table_selector: Any | None=None) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
