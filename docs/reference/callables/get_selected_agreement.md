# get_selected_agreement

Return the agreement selected by widget_select_agreement.

## What this is for and when to use it

Return the agreement selected by widget_select_agreement.

- Use immediately after widget_select_agreement to retrieve the selected agreement record for pipeline logic and evidence binding.

## When not to use it

- Do not use before rendering and completing widget_select_agreement, or as a substitute for querying all agreement metadata.

## Example

```python
agreement = get_selected_agreement()
dataset_name = agreement["dataset_name"]
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
      <td data-label="Parameter">—</td>
      <td data-label="Required">—</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Selected agreement dictionary for the active notebook session.

## Errors and side effects

**Errors:** Raises an error when no agreement has been selected in the current session.

**Side effects:** Reads session/widget state only; it does not write metadata, tables, or files.

## Related functions

- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Source

- Source file path: `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/data_agreement.py#L1083-L1098">View get_selected_agreement on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def get_selected_agreement() -> dict[str, Any]:
    """Return the agreement selected by :func:`widget_select_agreement`.

    Returns
    -------
    dict[str, Any]
        Selected latest-version agreement row.

    Raises
    ------
    RuntimeError
        If no selector has established a selected agreement.
    """
    if not _SELECTED_AGREEMENT:
        raise RuntimeError("No agreement selected. Run widget_select_agreement(...) first.")
    return dict(_SELECTED_AGREEMENT)
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.get_selected_agreement`
- Short name: `get_selected_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1083`
- Inbound references count: 0
- Outbound references count: 0

### AI implementation contract

- **required_context:** Depends on a prior widget_select_agreement call in the same notebook session and agreement metadata loaded via 00_env_config routing.
- **inputs:** No required parameters; reads the current in-memory widget selection state.
- **output:** Selected agreement dictionary for the active notebook session.
- **side_effects:** Reads session/widget state only; it does not write metadata, tables, or files.
- **failure_modes:** Raises an error when no agreement has been selected in the current session.
- **verification:** Verify the returned agreement has the expected dataset/table identifiers before using it to drive reads, writes, or governance evidence.

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/data_agreement.py#L1083-L1098">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/data_agreement.py#L1083-L1098</a>
- Start line: `1083`
- End line: `1098`
- Signature:

```python
def get_selected_agreement() -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

### Internal implementation helpers

Not documented yet

</details>
