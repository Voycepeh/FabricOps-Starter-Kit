# write_lakehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Purpose

Write a DataFrame to a configured Fabric lakehouse target.

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_lakehouse_table`
- Short name: `write_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#write_lakehouse_table">Module source anchor</a>
- Inbound references count: 6
- Outbound references count: 1

## Inbound references
- <a href="../internal/data_agreement/_ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement/_write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/governance_review/_setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../internal/metadata/_register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata/_setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

## Outbound references
- <a href="../internal/config/_get_store/"><code>fabricops_kit.config._get_store</code></a>
