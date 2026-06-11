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

- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _read_metadata_rows(config: Any, env: str, table: str, *, spark_session: Any) -> list[dict[str, Any]]
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
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/governance_review.py#L863-L864">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../internal/governance_review__review_governance_evidence/"><code>fabricops_kit.governance_review._review_governance_evidence</code></a>

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
