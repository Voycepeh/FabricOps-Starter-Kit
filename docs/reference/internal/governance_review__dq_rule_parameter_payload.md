# _dq_rule_parameter_payload

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

## Purpose

Return rule parameters stored inside ``rule_parameters_json``.

## Signature if available

```python
def _dq_rule_parameter_payload(rule: dict[str, Any], columns: list[str]) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._dq_rule_parameter_payload`
- Short name: `_dq_rule_parameter_payload`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/governance_review.py#L426-L448">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>
