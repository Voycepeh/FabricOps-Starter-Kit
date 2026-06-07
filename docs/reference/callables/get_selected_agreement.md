# get_selected_agreement

**Module:** `data_agreement`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use immediately after widget_select_agreement to retrieve the selected agreement record for pipeline logic and evidence binding.

## When not to use this

Do not use before rendering and completing widget_select_agreement, or as a substitute for querying all agreement metadata.

## Quick example

agreement = get_selected_agreement()
dataset_name = agreement["dataset_name"]

## Signature

```python
def get_selected_agreement() -> dict[str, Any]
```

## Parameters

No required parameters; reads the current in-memory widget selection state.

## Returns

Selected agreement dictionary for the active notebook session.

## Raises

Raises an error when no agreement has been selected in the current session.

## Side effects

Reads session/widget state only; it does not write metadata, tables, or files.

## FabricOps context

Depends on a prior widget_select_agreement call in the same notebook session and agreement metadata loaded via 00_env_config routing.

## AI implementation contract

- **required_context:** Depends on a prior widget_select_agreement call in the same notebook session and agreement metadata loaded via 00_env_config routing.
- **inputs:** No required parameters; reads the current in-memory widget selection state.
- **output:** Selected agreement dictionary for the active notebook session.
- **side_effects:** Reads session/widget state only; it does not write metadata, tables, or files.
- **failure_modes:** Raises an error when no agreement has been selected in the current session.
- **verification:** Verify the returned agreement has the expected dataset/table identifiers before using it to drive reads, writes, or governance evidence.

## Related functions

- <a href="../widget_select_agreement/"><code>fabricops_kit.data_agreement.widget_select_agreement</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#get_selected_agreement">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.get_selected_agreement`
- Short name: `get_selected_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Inbound references count: 0
- Outbound references count: 0

_No inbound or outbound references detected._
