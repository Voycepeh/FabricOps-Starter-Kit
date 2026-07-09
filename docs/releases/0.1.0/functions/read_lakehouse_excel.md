<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_excel`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_excel.read_lakehouse_excel`

Source path: `src/fabricops_kit/io/read_lakehouse_excel.py`

Signature: `read_lakehouse_excel(relative_path: 'str', *, target: 'str' = 'source', sheet_name=0, spark_session=None, context: 'dict[str, Any] | None' = None, **read_excel_kwargs)`

## Description

Read an Excel workbook from a configured Fabric-resolved path.

## Parameters

relative_path : str
    Excel file path resolved by the Fabric resolver.
target : str, default="source"
    Logical lakehouse target from ``00_env_config``.
sheet_name : str or int, default=0
    Worksheet name or index to read.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**read_excel_kwargs
    Additional keyword arguments passed to ``pandas.read_excel``.

## Return value

pyspark.sql.DataFrame
    Spark DataFrame converted from the selected Excel worksheet.

## Usage notes

FabricOps resolves the configured Lakehouse Files path from
``00_env_config``, reads the workbook binary through Spark, parses it with
``pandas.read_excel``, and converts the pandas DataFrame back to a Spark
DataFrame.

[Back to release overview](../index.md)
