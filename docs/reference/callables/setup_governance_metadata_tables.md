# setup_governance_metadata_tables

**Module:** `governance_review`  
**Classification:** Essential

## Purpose

Create or validate catalogue, lineage, context, rule, and classification tables during 00_env_config.

## Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.setup_governance_metadata_tables`
- Short name: `setup_governance_metadata_tables`
- Module: `governance_review`
- Classification: Essential
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source reference: <a href="../../api/modules/governance_review/#setup_governance_metadata_tables">Module source anchor</a>
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/governance_review/_coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>
- <a href="../get_governance_metadata_schemas/"><code>fabricops_kit.governance_review.get_governance_metadata_schemas</code></a>
