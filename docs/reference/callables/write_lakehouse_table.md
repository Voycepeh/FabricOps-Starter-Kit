# write_lakehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Write a DataFrame to a configured Fabric lakehouse target.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def write_lakehouse_table(df, config, env, target, table, mode='append', partition_by=None, repartition_by=None, overwrite_schema=True)
```

## Parameters

df : pyspark.sql.DataFrame
    Spark DataFrame to write.
config : FrameworkConfig | dict
    FabricOps FrameworkConfig or compatible config object.
env : str
    Environment key such as `"dev"`.
target : str
    Logical target name such as `"source"` or `"unified"`.
table : str
    Target table name under the lakehouse `Tables` area.
mode : str, default "append"
    Spark write mode. Supported values are `"append"`, `"overwrite"`,
    `"errorifexists"`, and `"ignore"`.
partition_by : str or list[str], optional
    Column or columns used to physically partition the Delta table.
repartition_by : int, str, list, or tuple, optional
    Optional repartitioning before write.
overwrite_schema : bool, default True
    Whether to set Spark Delta `overwriteSchema=true` before saving.

## Returns

None
    The DataFrame is written to the target Delta table path.

## Raises

ValueError
    If `table` is missing, `mode` is invalid, or the resolved target is not a lakehouse.

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline`; segment: `Fabric IO`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#write_lakehouse_table">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_lakehouse_table`
- Short name: `write_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 6
- Outbound references count: 1

## Inbound references
- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
