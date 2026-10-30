<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_csv`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_csv.read_lakehouse_csv`

Source path: `src/fabricops_kit/io/read_lakehouse_csv.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/io/read_lakehouse_csv.py)

Signature: `read_lakehouse_csv(relative_path: 'str', *, store: 'str' = 'Bronze', header: 'bool' = True, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read CSV files from a configured Lakehouse Files location.

## Parameters

relative_path : str
    Relative CSV file or folder path resolved underneath the configured
    Lakehouse ``Files`` area.
store : str, default="Bronze"
    Logical Lakehouse store key from ``00_env_config``. It is not necessarily
    the literal physical Lakehouse name.
header : bool, default=True
    Whether Spark should treat the first row as column names. When
    ``header=True``, the first row is used as column names. When
    ``header=False``, the first row is treated as data and Spark typically
    creates generic column names such as ``_c0``, ``_c1``, and ``_c2``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Spark CSV reader options passed directly to Spark's CSV
    reader, such as ``inferSchema``, ``sep``, ``quote``, ``escape``,
    ``encoding``, ``multiLine``, ``dateFormat``, ``timestampFormat``,
    ``nullValue``, ``mode``, and ``recursiveFileLookup``. FabricOps does
    not interpret or transform these options beyond forwarding them.

## Return value

pyspark.sql.DataFrame
    A lazy Spark DataFrame representing the CSV file or compatible CSV
    files found at the resolved Lakehouse ``Files`` path. Column types
    follow Spark CSV reader behavior and generally remain strings unless
    schema inference or other schema handling is explicitly requested.

## Usage notes

The Spark DataFrame is lazy; downstream actions evaluate the read. Additional
reader options are forwarded to Spark. Folder compatibility and malformed
record handling follow Spark CSV options.

[Back to release overview](../index.md)
