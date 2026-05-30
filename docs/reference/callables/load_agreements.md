# load_agreements

**Module:** `data_agreement`  
**Classification:** Essential

## Purpose

Load latest versioned agreement rows from the configured metadata lakehouse.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.load_agreements`
- Short name: `load_agreements`
- Module: `data_agreement`
- Classification: Essential
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#load_agreements">Module source anchor</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../create_agreement_form/"><code>fabricops_kit.data_agreement.create_agreement_form</code></a>
- <a href="../render_agreement_intake_app/"><code>fabricops_kit.data_agreement.render_agreement_intake_app</code></a>

## Outbound references
- <a href="../latest_agreement_versions/"><code>fabricops_kit.data_agreement.latest_agreement_versions</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
