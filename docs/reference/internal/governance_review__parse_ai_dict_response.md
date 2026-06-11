# _parse_ai_dict_response

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__extract_assignment_payload/"><code>fabricops_kit.governance_review._extract_assignment_payload</code></a>

## Purpose

Parse JSON/Python-dict AI response text into a dictionary.

## Signature if available

```python
def _parse_ai_dict_response(text: str) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._parse_ai_dict_response`
- Short name: `_parse_ai_dict_response`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/governance_review.py#L1149-L1164">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/governance_review__extract_assignment_payload/"><code>fabricops_kit.governance_review._extract_assignment_payload</code></a>
