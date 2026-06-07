# _run_fabric_ai_drafting

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__draft_business_context/"><code>fabricops_kit.governance_review._draft_business_context</code></a>
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>
- <a href="../internal/governance_review__draft_governance/"><code>fabricops_kit.governance_review._draft_governance</code></a>

## Purpose

Run Fabric AI prompt drafting against prepared profile rows.

## Signature if available

```python
def _run_fabric_ai_drafting(prepared_profile_df, *, prompt: str, output_col: str)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._run_fabric_ai_drafting`
- Short name: `_run_fabric_ai_drafting`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L602-L607">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 0

## Inbound references
- <a href="../internal/governance_review__draft_business_context/"><code>fabricops_kit.governance_review._draft_business_context</code></a>
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>
- <a href="../internal/governance_review__draft_governance/"><code>fabricops_kit.governance_review._draft_governance</code></a>
