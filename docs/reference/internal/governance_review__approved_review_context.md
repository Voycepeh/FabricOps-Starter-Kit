# _approved_review_context

**Module:** `governance_review`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _approved_review_context(profile_rows: list[dict[str, Any]], *, config: Any=None, env: str | None=None, approved_by: str | None=None) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review._approved_review_context`
- Short name: `_approved_review_context`
- Module: `governance_review`
- Classification: Internal
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/governance_review.py#L82-L85">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 4

## Inbound references
- <a href="../internal/governance_review__build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review__build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review__build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>

## Outbound references
- <a href="../internal/governance_review__value/"><code>fabricops_kit.governance_review._value</code></a>
- <a href="../internal/metadata__build_runtime_audit_fields/"><code>fabricops_kit.metadata._build_runtime_audit_fields</code></a>
- <a href="../internal/metadata__now_utc_iso/"><code>fabricops_kit.metadata._now_utc_iso</code></a>
- <a href="../internal/metadata__resolve_action_by/"><code>fabricops_kit.metadata._resolve_action_by</code></a>
