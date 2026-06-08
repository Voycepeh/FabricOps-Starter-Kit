# _extract_assignment_payload

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>

## Purpose

Extract dictionary payloads from AI response rows with optional table-key narrowing.

## Signature if available

```python
def _extract_assignment_payload(response_rows, *, response_col: str, assignment_key: str | None=None, table_name: str | None=None) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._extract_assignment_payload`
- Short name: `_extract_assignment_payload`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/01cad12186fe15942524ddfa6effa011f04aecb5/src/fabricops_kit/governance_review.py#L640-L654">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
- <a href="../internal/governance_review__parse_ai_dict_response/"><code>fabricops_kit.governance_review._parse_ai_dict_response</code></a>
