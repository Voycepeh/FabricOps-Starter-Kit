# enforce_dq_rules

**Module:** `governance_review`  
**Classification:** Callable

## Purpose

Enforce approved active DQ rules as a target-write guardrail without filtering rows.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.enforce_dq_rules`
- Short name: `enforce_dq_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#enforce_dq_rules">Module source anchor</a>
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review/_load_active_dq_rules/"><code>fabricops_kit.governance_review._load_active_dq_rules</code></a>
- <a href="../internal/governance_review/_run_dq_guardrail_checks/"><code>fabricops_kit.governance_review._run_dq_guardrail_checks</code></a>
- <a href="../internal/governance_review/_summarize_dq_guardrail/"><code>fabricops_kit.governance_review._summarize_dq_guardrail</code></a>
