# _draft_dq_rules

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

Draft candidate DQ rules from metadata profiles or a raw DataFrame fallback.

## Signature if available

```python
def _draft_dq_rules(*, profile_df=None, df=None, table_name: str, business_context: str='', prompt_template: str | None=None, output_col: str='response') -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._draft_dq_rules`
- Short name: `_draft_dq_rules`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#_draft_dq_rules">Module source anchor</a>
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
- <a href="../internal/governance_review__extract_assignment_payload/"><code>fabricops_kit.governance_review._extract_assignment_payload</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../internal/governance_review__run_fabric_ai_drafting/"><code>fabricops_kit.governance_review._run_fabric_ai_drafting</code></a>
