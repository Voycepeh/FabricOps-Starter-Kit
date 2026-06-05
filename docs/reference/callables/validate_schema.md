# validate_schema

**Module:** `schema_contracts`  
**Classification:** Optional

## Purpose

Validate a Spark DataFrame shape against approved dataset-level schema contract columns without enforcement or metadata writes.

## Function manifest

- Fully qualified function name: `fabricops_kit.schema_contracts.validate_schema`
- Short name: `validate_schema`
- Module: `schema_contracts`
- Classification: Optional
- Related module: `schema_contracts`
- Source file path: `src/fabricops_kit/schema_contracts.py`
- Source reference: <a href="../../api/modules/schema_contracts/#validate_schema">Module source anchor</a>
- Inbound references count: 1
- Outbound references count: 5

## Inbound references
- <a href="../apply_schema_guardrail/"><code>fabricops_kit.schema_contracts.apply_schema_guardrail</code></a>

## Outbound references
- <a href="../internal/schema_contracts/_bool/"><code>fabricops_kit.schema_contracts._bool</code></a>
- <a href="../internal/schema_contracts/_coerce_rows/"><code>fabricops_kit.schema_contracts._coerce_rows</code></a>
- <a href="../internal/schema_contracts/_get_any/"><code>fabricops_kit.schema_contracts._get_any</code></a>
- <a href="../internal/schema_contracts/_normalize_spark_data_type/"><code>fabricops_kit.schema_contracts._normalize_spark_data_type</code></a>
- <a href="../internal/schema_contracts/_schema_rows_from_dataframe/"><code>fabricops_kit.schema_contracts._schema_rows_from_dataframe</code></a>
