# record_table_governance

**Module:** `governance_review`  
**Classification:** Callable

## Purpose

Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.record_table_governance`
- Short name: `record_table_governance`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#record_table_governance">Module source anchor</a>
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review/_build_classification_records/"><code>fabricops_kit.governance_review._build_classification_records</code></a>
- <a href="../internal/governance_review/_build_column_context_records/"><code>fabricops_kit.governance_review._build_column_context_records</code></a>
- <a href="../internal/governance_review/_build_dq_rule_records/"><code>fabricops_kit.governance_review._build_dq_rule_records</code></a>
