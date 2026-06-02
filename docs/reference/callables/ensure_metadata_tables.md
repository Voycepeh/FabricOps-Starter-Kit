# ensure_metadata_tables

**Module:** `data_agreement`  
**Classification:** Optional

## Purpose

Idempotently create or validate the lightweight 01_da metadata tables.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.ensure_metadata_tables`
- Short name: `ensure_metadata_tables`
- Module: `data_agreement`
- Classification: Optional
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#ensure_metadata_tables">Module source anchor</a>
- Inbound references count: 1
- Outbound references count: 6

## Inbound references
- <a href="../setup_data_agreement_tables/"><code>fabricops_kit.data_agreement.setup_data_agreement_tables</code></a>

## Outbound references
- <a href="../internal/data_agreement/_column_names/"><code>fabricops_kit.data_agreement._column_names</code></a>
- <a href="../internal/data_agreement/_table_name/"><code>fabricops_kit.data_agreement._table_name</code></a>
- <a href="../get_data_agreement_schema/"><code>fabricops_kit.data_agreement.get_data_agreement_schema</code></a>
- <a href="../get_data_steward_schema/"><code>fabricops_kit.data_agreement.get_data_steward_schema</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
