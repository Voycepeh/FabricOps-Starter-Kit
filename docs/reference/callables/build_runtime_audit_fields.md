# build_runtime_audit_fields

**Module:** `metadata`  
**Classification:** Essential

## Purpose

Build shared runtime audit values; 03_pc uses notebook and committed-by context while adding dataframe audit columns inline.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata.build_runtime_audit_fields`
- Short name: `build_runtime_audit_fields`
- Module: `metadata`
- Classification: Essential
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="../../api/modules/metadata/#build_runtime_audit_fields">Module source anchor</a>
- Inbound references count: 3
- Outbound references count: 3

## Inbound references
- <a href="../internal/data_agreement/_create_or_update_data_agreement/"><code>fabricops_kit.data_agreement._create_or_update_data_agreement</code></a>
- <a href="../internal/data_agreement/_create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement/_save_agreement_evidence_records/"><code>fabricops_kit.data_agreement._save_agreement_evidence_records</code></a>

## Outbound references
- <a href="../internal/metadata/_context_get/"><code>fabricops_kit.metadata._context_get</code></a>
- <a href="../internal/metadata/_runtime_context/"><code>fabricops_kit.metadata._runtime_context</code></a>
- <a href="../internal/metadata/_safe_str/"><code>fabricops_kit.metadata._safe_str</code></a>
