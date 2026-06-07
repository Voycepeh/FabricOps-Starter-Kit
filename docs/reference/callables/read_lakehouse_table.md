# read_lakehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use when reading a Delta table from a configured Fabric lakehouse target.

## When not to use this

Do not use for lakehouse Files CSV, Parquet, or Excel paths, or for warehouse SQL tables.

## Quick example

df = read_lakehouse_table(CONFIG, env="Sandbox", target="Source", table="orders", spark_session=spark)

## Signature

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

## Parameters

config, env, target, table, optional schema, verbose flag, and spark_session.

## Returns

Spark DataFrame loaded from the configured lakehouse table.

## Raises

Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.

## Side effects

Reads from a lakehouse table; it does not write metadata, tables, or files.

## FabricOps context

Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.

## AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, table, optional schema, verbose flag, and spark_session.
- **output:** Spark DataFrame loaded from the configured lakehouse table.
- **side_effects:** Reads from a lakehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark, or table-read errors when the target or table cannot be resolved/read.
- **verification:** Verify the target/table name comes from CONFIG and check the returned DataFrame schema or row count before downstream transformations.

## Related functions

- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_lakehouse_table">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_table`
- Short name: `read_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 9
- Outbound references count: 2

## Inbound references
- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
