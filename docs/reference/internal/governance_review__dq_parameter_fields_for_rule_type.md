# _dq_parameter_fields_for_rule_type

**Module:** `governance_review`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../widget_review_dq_rules/"><code>fabricops_kit.governance_review.widget_review_dq_rules</code></a>

## Purpose

Return parameter names a reviewer should fill for a rule type.

## Signature if available

```python
def _dq_parameter_fields_for_rule_type(rule_type: str) -> list[str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._dq_parameter_fields_for_rule_type`
- Short name: `_dq_parameter_fields_for_rule_type`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a212c94775e71b6e429e41b51fbc57ac733903cb/src/fabricops_kit/governance_review.py#L624-L642">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../widget_review_dq_rules/"><code>fabricops_kit.governance_review.widget_review_dq_rules</code></a>

## Outbound references
- <a href="../internal/governance_review__canonical_dq_rule_type/"><code>fabricops_kit.governance_review._canonical_dq_rule_type</code></a>
