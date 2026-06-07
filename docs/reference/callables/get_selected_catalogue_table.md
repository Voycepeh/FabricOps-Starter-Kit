# get_selected_catalogue_table

Return the table selected by widget_select_catalogue_table.

## Use this when

Return the table selected by widget_select_catalogue_table.

## Do not use this for

Not documented yet

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
      <th>What it means</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>table_selector</code></td>
      <td data-label="Required">No</td>
      <td data-label="What it means">Selector returned by ``widget_select_catalogue_table``. Passing it is optional because the widget also maintains module-level selection state.</td>
    </tr>
  </tbody>
</table>
</div>

<details class="reference-signature-details">
<summary>Full signature</summary>

```python
def get_selected_catalogue_table(table_selector: Any | None=None) -> dict[str, Any]
```

</details>

## Output

dict[str, Any]
    Stable table identity used by ``load_catalogue_profile_rows``.

## Raises

Not documented yet

## Side effects

Not documented yet

## Related functions

Not documented yet

<details class="reference-metadata-details">
<summary>AI implementation contract</summary>

These fields are generated for agents and maintainers, not for quick-start reading.

- **required_context:** Starter template: `03_review`; segment: `Governance review`.
- **inputs:** table_selector : ipywidgets.Combobox, optional
    Selector returned by ``widget_select_catalogue_table``. Passing it is
    optional because the widget also maintains module-level selection state.
- **output:** dict[str, Any]
    Stable table identity used by ``load_catalogue_profile_rows``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

</details>

<details class="reference-metadata-details">
<summary>Function manifest</summary>

- Fully qualified function name: `fabricops_kit.governance_review.get_selected_catalogue_table`
- Short name: `get_selected_catalogue_table`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `261`
- Inbound references count: 0
- Outbound references count: 0

</details>

<details class="reference-metadata-details">
<summary>Raw inbound and outbound references</summary>

### Inbound references

Not documented yet

### Outbound references

Not documented yet

</details>

## Source code

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b6a5693130e525f919566c2115ac67da9c6faef/src/fabricops_kit/governance_review.py#L261-L285">View get_selected_catalogue_table on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

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

</details>
