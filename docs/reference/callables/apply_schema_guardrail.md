# apply_schema_guardrail

**Module:** `schema_contracts`  
**Classification:** Essential

## Purpose

Load the approved dataset contract, validate schema drift, enforce observe/warn/fail behavior, and write evidence.

## Function manifest

- Fully qualified function name: `fabricops_kit.schema_contracts.apply_schema_guardrail`
- Short name: `apply_schema_guardrail`
- Module: `schema_contracts`
- Classification: Essential
- Related module: `schema_contracts`
- Source file path: `src/fabricops_kit/schema_contracts.py`
- Source reference: <a href="../../api/modules/schema_contracts/#apply_schema_guardrail">Module source anchor</a>
- Inbound references count: 0
- Outbound references count: 7

## Outbound references
- <a href="../SchemaContractValidationError/"><code>fabricops_kit.schema_contracts.SchemaContractValidationError</code></a>
- <a href="../internal/schema_contracts/_build_schema_validation_evidence/"><code>fabricops_kit.schema_contracts._build_schema_validation_evidence</code></a>
- <a href="../internal/schema_contracts/_enforce_schema_result/"><code>fabricops_kit.schema_contracts._enforce_schema_result</code></a>
- <a href="../internal/schema_contracts/_get_active_spark/"><code>fabricops_kit.schema_contracts._get_active_spark</code></a>
- <a href="../internal/schema_contracts/_load_schema_contract/"><code>fabricops_kit.schema_contracts._load_schema_contract</code></a>
- <a href="../internal/schema_contracts/_write_schema_validation_evidence/"><code>fabricops_kit.schema_contracts._write_schema_validation_evidence</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.schema_contracts.validate_schema</code></a>
