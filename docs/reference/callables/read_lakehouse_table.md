# read_lakehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Read a table from a configured Fabric lakehouse target.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def read_lakehouse_table(config, env, target, table, spark_session=None)
```

## Parameters

config : FrameworkConfig | dict
    FabricOps FrameworkConfig or compatible config object.
env : str
    Environment key such as `"dev"`.
target : str
    Logical target name such as `"source"` or `"unified"`.
table : str
    Table name under the lakehouse `Tables` area.
spark_session : object, optional
    Spark session to use. If omitted, the helper uses the notebook global
    `spark`.

## Returns

pyspark.sql.DataFrame
    Spark DataFrame loaded from the Delta table.

## Raises

ValueError
    If `table` is missing or the resolved target is not a lakehouse.
RuntimeError
    If no Spark session is available.

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline / optional 99_explore`; segment: `Fabric IO`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__list_all_data_agreement_rows/"><code>fabricops_kit.data_agreement._list_all_data_agreement_rows</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../load_catalogue_profile_rows/"><code>fabricops_kit.governance_review.load_catalogue_profile_rows</code></a>
- <a href="../widget_select_catalogue_table/"><code>fabricops_kit.governance_review.widget_select_catalogue_table</code></a>
- <a href="../internal/metadata__load_notebook_registry/"><code>fabricops_kit.metadata._load_notebook_registry</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>

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
