# _draft_governance

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

Draft sensitivity and PII classification suggestions with Fabric AI.

## Signature if available

```python
def _draft_governance(prepared_profile_df, prompt: str | None=None, output_col: str='ai_governance_response')
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._draft_governance`
- Short name: `_draft_governance`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/8f8ba1a4c1e063896508520952dedc3eda348629/src/fabricops_kit/governance_review.py#L1143-L1145">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 1

## Outbound references
- <a href="../internal/governance_review__run_fabric_ai_drafting/"><code>fabricops_kit.governance_review._run_fabric_ai_drafting</code></a>
