# create_or_update_data_steward

**Module:** `data_agreement`  
**Classification:** Optional

## Purpose

Append a created or updated steward assignment with runtime audit fields.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.create_or_update_data_steward`
- Short name: `create_or_update_data_steward`
- Module: `data_agreement`
- Classification: Optional
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="../../api/modules/data_agreement/#create_or_update_data_steward">Module source anchor</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../internal/data_agreement/_render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>

## Outbound references
- <a href="../internal/data_agreement/_table_name/"><code>fabricops_kit.data_agreement._table_name</code></a>
- <a href="../internal/data_agreement/_write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../serialize_custom_fields/"><code>fabricops_kit.data_agreement.serialize_custom_fields</code></a>
- <a href="../build_runtime_audit_fields/"><code>fabricops_kit.metadata.build_runtime_audit_fields</code></a>
