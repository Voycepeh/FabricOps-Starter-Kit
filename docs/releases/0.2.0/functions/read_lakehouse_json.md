<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_json`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_json.read_lakehouse_json`

Source path: `src/fabricops_kit/io/read_lakehouse_json.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/io/read_lakehouse_json.py)

Signature: `read_lakehouse_json(relative_path: 'str', *, store: 'str' = 'Bronze', spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read JSON data from a configured Lakehouse ``Files`` path through Spark.

## Parameters

relative_path : str
    JSON file or folder path underneath the configured Lakehouse ``Files``
    area. Root-level and nested paths are supported.
store : str, default="Bronze"
    Logical Lakehouse store key configured by ``00_env_config``.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Options forwarded unchanged to Spark's JSON reader, such as
    ``multiLine``, ``mode``, ``columnNameOfCorruptRecord``, ``dateFormat``,
    ``timestampFormat``, ``encoding``, ``recursiveFileLookup``,
    ``pathGlobFilter``, ``primitivesAsString``, ``allowComments``,
    ``allowSingleQuotes``, and ``allowUnquotedFieldNames``.

## Return value

pyspark.sql.DataFrame
    A lazy Spark DataFrame backed by the resolved JSON file or compatible
    files in the supplied folder path.

## Usage notes

Spark normally treats each line as a separate JSON record (JSON Lines or
newline-delimited JSON). Standard multi-line JSON documents may require
``multiLine=True``. Folder paths are passed directly to Spark; FabricOps
does not iterate through files or eagerly validate or collect the data.

[Back to release overview](../index.md)
