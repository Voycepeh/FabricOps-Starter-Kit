# list_data_agreements

**Module:** `data_agreement`  
**Classification:** Optional

## Purpose

List latest agreement versions from the configured metadata lakehouse.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.list_data_agreements`
- Short name: `list_data_agreements`
- Module: `data_agreement`
- Classification: Optional
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#list_data_agreements">Module source anchor</a>
- Inbound references count: 2
- Outbound references count: 3

## Inbound references
- <a href="../internal/data_agreement/_render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>
- <a href="../load_agreements/"><code>fabricops_kit.data_agreement.load_agreements</code></a>

## Outbound references
- <a href="../internal/data_agreement/_table_name/"><code>fabricops_kit.data_agreement._table_name</code></a>
- <a href="../internal/data_agreement/latest_agreement_versions/"><code>fabricops_kit.data_agreement.latest_agreement_versions</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
