# _validate_dq_rules

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>
- <a href="../internal/governance_review__dq_failed_expression/"><code>fabricops_kit.governance_review._dq_failed_expression</code></a>
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__parse_dq_ai_suggestions/"><code>fabricops_kit.governance_review._parse_dq_ai_suggestions</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../widget_review_dq_rules/"><code>fabricops_kit.governance_review.widget_review_dq_rules</code></a>

## Purpose

Validate canonical DQ rules before loading or enforcement.

## Signature if available

```python
def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._validate_dq_rules`
- Short name: `_validate_dq_rules`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/governance_review.py#L1184-L1257">View source on GitHub</a>
- Inbound references count: 7
- Outbound references count: 1

## Inbound references
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>
- <a href="../internal/governance_review__dq_failed_expression/"><code>fabricops_kit.governance_review._dq_failed_expression</code></a>
- <a href="../internal/governance_review__draft_dq_rules/"><code>fabricops_kit.governance_review._draft_dq_rules</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__parse_dq_ai_suggestions/"><code>fabricops_kit.governance_review._parse_dq_ai_suggestions</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../widget_review_dq_rules/"><code>fabricops_kit.governance_review.widget_review_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
