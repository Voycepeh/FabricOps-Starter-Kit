# read_lakehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Purpose

Read a table from a configured Fabric lakehouse target.

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_table`
- Short name: `read_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_lakehouse_table">Module source anchor</a>
- Inbound references count: 9
- Outbound references count: 2

## Inbound references
- <a href="../internal/data_agreement/_ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement/_list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement/_list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/governance_review/_setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../internal/metadata/_load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata/_setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

## Outbound references
- <a href="../internal/config/_get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output/_get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
