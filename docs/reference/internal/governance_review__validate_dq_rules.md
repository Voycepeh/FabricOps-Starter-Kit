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

- <a href="../internal/governance_review__enforce_dq/"><code>fabricops_kit.governance_review._enforce_dq</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__run_dq_rules/"><code>fabricops_kit.governance_review._run_dq_rules</code></a>
- <a href="../internal/governance_review__split_dq_rows/"><code>fabricops_kit.governance_review._split_dq_rows</code></a>

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
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/acd9c065e2cac26ab9378c11c224ee1b7fb00ba7/src/fabricops_kit/governance_review.py#L882-L909">View source on GitHub</a>
- Inbound references count: 5
- Outbound references count: 1

## Inbound references
- <a href="../internal/governance_review__enforce_dq/"><code>fabricops_kit.governance_review._enforce_dq</code></a>
- <a href="../internal/governance_review__load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review__run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review__run_dq_rules/"><code>fabricops_kit.governance_review._run_dq_rules</code></a>
- <a href="../internal/governance_review__split_dq_rows/"><code>fabricops_kit.governance_review._split_dq_rows</code></a>

## Outbound references
- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
