# _draft_business_context

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

Draft column business-context suggestions with Fabric AI.

## Signature if available

```python
def _draft_business_context(prepared_profile_df, prompt_template: str=BUSINESS_CONTEXT_PROMPT, output_col: str='ai_business_context_response')
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._draft_business_context`
- Short name: `_draft_business_context`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/governance_review.py#L610-L612">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 1

## Outbound references
- <a href="../internal/governance_review__run_fabric_ai_drafting/"><code>fabricops_kit.governance_review._run_fabric_ai_drafting</code></a>
