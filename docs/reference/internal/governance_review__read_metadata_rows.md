# _read_metadata_rows

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../review_pipeline_run/"><code>fabricops_kit.governance_review.review_pipeline_run</code></a>

## Purpose

Read metadata rows from the configured metadata lakehouse target.

## Signature if available

```python
def _read_metadata_rows(config: Any, env: str, table_name: str, *, spark_session: Any, missing_ok: bool=True) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._read_metadata_rows`
- Short name: `_read_metadata_rows`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#_read_metadata_rows">Module source anchor</a>
- Inbound references count: 1
- Outbound references count: 3

## Inbound references
- <a href="../review_pipeline_run/"><code>fabricops_kit.governance_review.review_pipeline_run</code></a>

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
- <a href="../internal/governance_review__is_table_not_found_error/"><code>fabricops_kit.governance_review._is_table_not_found_error</code></a>
