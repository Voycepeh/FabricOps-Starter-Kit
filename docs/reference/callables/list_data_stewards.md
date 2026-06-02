# list_data_stewards

**Module:** `data_agreement`  
**Classification:** Optional

## Purpose

List latest steward assignments, optionally filtering to active rows.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.list_data_stewards`
- Short name: `list_data_stewards`
- Module: `data_agreement`
- Classification: Optional
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#list_data_stewards">Module source anchor</a>
- Inbound references count: 4
- Outbound references count: 4

## Inbound references
- <a href="../internal/data_agreement/_render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../create_or_update_data_agreement/"><code>fabricops_kit.data_agreement.create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement/load_active_data_steward_profiles/"><code>fabricops_kit.data_agreement.load_active_data_steward_profiles</code></a>
- <a href="../setup_data_agreement_tables/"><code>fabricops_kit.data_agreement.setup_data_agreement_tables</code></a>

## Outbound references
- <a href="../internal/data_agreement/_active_steward/"><code>fabricops_kit.data_agreement._active_steward</code></a>
- <a href="../internal/data_agreement/_latest_by_key/"><code>fabricops_kit.data_agreement._latest_by_key</code></a>
- <a href="../internal/data_agreement/_table_name/"><code>fabricops_kit.data_agreement._table_name</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
