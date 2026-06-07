# widget_review_column_classification

**Module:** `governance_review`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Render standalone sensitivity and PII classification review guidance for selected profile rows.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def widget_review_column_classification(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]
```

## Parameters

profile_rows : list of dict
    Selected column profile evidence from ``load_catalogue_profile_rows``.

## Returns

list[dict[str, Any]]
    Empty editable review list. Add approved classification dictionaries
    before calling ``record_table_governance``.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `03_review`; segment: `Governance review`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/governance_review__display_review_guidance/"><code>fabricops_kit.governance_review._display_review_guidance</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#widget_review_column_classification">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_review_column_classification`
- Short name: `widget_review_column_classification`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Inbound references count: 0
- Outbound references count: 1

## Outbound references
- <a href="../internal/governance_review__display_review_guidance/"><code>fabricops_kit.governance_review._display_review_guidance</code></a>
