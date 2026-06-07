# read_lakehouse_parquet

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Read a Parquet path from a configured Fabric lakehouse Files path.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def read_lakehouse_parquet(config, env, target, relative_path, verbose=True, spark_session=None)
```

## Parameters

config : FrameworkConfig | dict
    FabricOps FrameworkConfig or compatible config object.
env : str
    Environment key such as `"dev"`.
target : str
    Logical target name such as `"source"` or `"unified"`.
relative_path : str
    Path to the Parquet file under the lakehouse `Files/` folder, without
    the leading `"Files/"`. For example:
    `"raw/orders/orders_2026.parquet"`.
verbose : bool, default True
    Whether to print read and fallback progress.
spark_session : object, optional
    Spark session to use. If omitted, the helper uses the notebook global
    `spark`.

## Returns

pyspark.sql.DataFrame
    Spark DataFrame loaded from the original or converted Parquet path.

## Raises

ValueError
    If `relative_path` is not a nested file path.
RuntimeError
    If neither the original path nor the converted fallback path can be
    read successfully.

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline / optional 99_explore`; segment: `Fabric IO`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__convert_single_parquet_ns_to_us/"><code>fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_lakehouse_parquet">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- Short name: `read_lakehouse_parquet`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__convert_single_parquet_ns_to_us/"><code>fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>
