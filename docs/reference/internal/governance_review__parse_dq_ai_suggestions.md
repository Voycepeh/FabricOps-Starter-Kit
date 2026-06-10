# _parse_dq_ai_suggestions

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

Not documented yet

## Purpose

Parse and validate draft AI DQ suggestions without approving them.

## Signature if available

```python
def _parse_dq_ai_suggestions(response_rows: Any, *, response_col: str='response', table_name: str | None=None) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._parse_dq_ai_suggestions`
- Short name: `_parse_dq_ai_suggestions`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/governance_review.py#L645-L659">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 3

## Outbound references
- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
- <a href="../internal/governance_review__extract_assignment_payload/"><code>fabricops_kit.governance_review._extract_assignment_payload</code></a>
- <a href="../internal/governance_review__validate_dq_rules/"><code>fabricops_kit.governance_review._validate_dq_rules</code></a>
