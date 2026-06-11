# _catalogue_table_options

**Module:** `governance_review`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>

## Purpose

Return one option per logical table using its latest successful profile.

## Signature if available

```python
def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._catalogue_table_options`
- Short name: `_catalogue_table_options`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/governance_review.py#L258-L307">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 3

## Inbound references
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>

## Outbound references
- <a href="../internal/governance_review__is_success/"><code>fabricops_kit.governance_review._is_success</code></a>
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
- <a href="../internal/metadata__build_metadata_table_key/"><code>fabricops_kit.metadata._build_metadata_table_key</code></a>
