# get_selected_agreement

Return the agreement selected by widget_select_agreement.

## Purpose

Return the agreement selected by widget_select_agreement.

## At a glance

**Use when:**

- Use immediately after widget_select_agreement to retrieve the selected agreement record for pipeline logic and evidence binding.

**Do not use when:**

- Do not use before rendering and completing widget_select_agreement, or as a substitute for querying all agreement metadata.

**Example:**

```python
agreement = get_selected_agreement()
dataset_name = agreement["dataset_name"]
```

**Errors:**

Raises an error when no agreement has been selected in the current session.

**Side effects:**

Reads session/widget state only; it does not write metadata, tables, or files.

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
      <td data-label="Parameter">—</td>
      <td data-label="Required">—</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
  </tbody>
</table>
</div>

## Returns

Selected agreement dictionary for the active notebook session.

## Used by

Not documented yet

## Calls

Not documented yet

## Implementation details

### Call flow

```text
get_selected_agreement(...)
```

## Public callable source code

- Source file path: `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/427905557f281c2de218c8d2213dc8798864c090/src/fabricops_kit/data_agreement.py#L1083-L1098">View get_selected_agreement on GitHub</a>

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

## Nested helper functions

??? info "Nested helper functions: 0"

    No nested helper functions were detected for `get_selected_agreement`.
    
    <div class="module-table-scroll reference-input-table">
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
          <td data-label="Helper">—</td>
          <td data-label="Role">No nested helper functions detected.</td>
          <td data-label="Source">—</td>
        </tr>
      </tbody>
    </table>
    </div>

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/427905557f281c2de218c8d2213dc8798864c090/src/fabricops_kit/data_agreement.py#L1083-L1098">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/427905557f281c2de218c8d2213dc8798864c090/src/fabricops_kit/data_agreement.py#L1083-L1098</a>
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

### Call flow

```text
get_selected_agreement(...)
```

</details>
