# read_lakehouse_excel

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Read an Excel file from a configured Fabric lakehouse Files path.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None, **read_excel_kwargs)
```

## Parameters

config : FrameworkConfig | dict
    FabricOps FrameworkConfig or compatible config object.
env : str
    Environment key such as `"dev"`.
target : str
    Logical target name such as `"source"` or `"unified"`.
relative_path : str
    Path to the Excel file relative to the lakehouse ``Files`` area, for
    example ``"reference/faculty_mapping.xlsx"``. A leading ``"Files/"``
    prefix is accepted for consistency with notebook examples and is
    normalized away before the lakehouse path is resolved.
sheet_name : str or int, default 0
    Worksheet name or index to read. Defaults to the first worksheet.
spark_session : object, optional
    Spark session to use. If omitted, the helper uses the notebook global
    `spark`.
**read_excel_kwargs
    Additional keyword arguments passed directly to
    :func:`pandas.read_excel`. Common options include ``skiprows`` for
    title rows above the real header, ``header`` for custom header-row
    selection, ``usecols`` for column filtering, ``dtype`` for mixed-type
    columns, and ``nrows`` for sampling or bounded reads.

## Returns

pyspark.sql.DataFrame
    Spark DataFrame converted from the selected Excel worksheet.

## Raises

ValueError
    If `relative_path` is missing or the resolved target is not a lakehouse.
FileNotFoundError
    If the Excel file cannot be found at the resolved lakehouse path.
RuntimeError
    If no Spark session is available.

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline / optional 99_explore`; segment: `Fabric IO`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_lakehouse_excel">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- Short name: `read_lakehouse_excel`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 0
- Outbound references count: 3

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>
