# get_selected_catalogue_table

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Return the table selected by widget_select_catalogue_table.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def get_selected_catalogue_table(table_selector: Any | None=None) -> dict[str, Any]
```

## Parameters

table_selector : ipywidgets.Combobox, optional
    Selector returned by ``widget_select_catalogue_table``. Passing it is
    optional because the widget also maintains module-level selection state.

## Returns

dict[str, Any]
    Stable table identity used by ``load_catalogue_profile_rows``.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `03_review`; segment: `Governance review`.

## AI implementation contract

Not documented yet

## Related functions

Not documented yet

## Source and tests

- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#get_selected_catalogue_table">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.get_selected_catalogue_table`
- Short name: `get_selected_catalogue_table`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Inbound references count: 0
- Outbound references count: 0

_No inbound or outbound references detected._
