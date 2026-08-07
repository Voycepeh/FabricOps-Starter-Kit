<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_parquet`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_parquet.read_lakehouse_parquet`

Source path: `src/fabricops_kit/io/read_lakehouse_parquet.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/io/read_lakehouse_parquet.py)

Signature: `read_lakehouse_parquet(relative_path: 'str', *, target: 'str' = 'source', verbose: 'bool' = True, spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read Parquet data from the configured Lakehouse ``Files`` area through Spark.

## Parameters

relative_path : str
    Parquet file path resolved underneath the configured Lakehouse
    ``Files`` area. Root-level files such as ``customers.parquet`` and
    nested paths such as ``incoming/2026/customers.parquet`` are
    supported.
target : str, default="source"
    Logical Lakehouse target from ``00_env_config``.
verbose : bool, default=True
    Whether to print operational progress for original path attempts,
    original read success or failure, ``_tsus`` path attempts, conversion
    attempts, and fallback success or failure. It does not change the
    resulting data.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Spark Parquet reader options forwarded to Spark's Parquet
    reader for the original path read, the existing ``_tsus`` path read,
    and the read after conversion. Representative options include
    ``mergeSchema``, ``recursiveFileLookup``, ``pathGlobFilter``,
    ``modifiedBefore``, and ``modifiedAfter``. FabricOps does not
    interpret these options.

## Return value

pyspark.sql.DataFrame
    A Spark DataFrame backed by either the original resolved Parquet path
    or the compatible ``_tsus`` fallback path. Before returning, the
    function executes a one-row Spark action to verify that the selected
    data can be decoded.

## Usage notes

Normal read flow:

``Configured Lakehouse Files path -> Spark Parquet read -> df.limit(1).collect() -> Return DataFrame when decoding succeeds``

Spark reads are normally lazy, but this function deliberately executes
``limit(1).collect()`` before returning. The validation action confirms
that Spark can decode at least one row. The function is therefore not a
purely lazy reader, but it does not collect the entire dataset to the
driver.

``target`` is a logical Lakehouse target from ``00_env_config`` and
``relative_path`` is resolved under the configured Lakehouse ``Files``
area. Root-level and nested paths are supported. The resolved location is
conceptually ``<configured lakehouse>/Files/<relative_path>``. Examples:

``df = read_lakehouse_parquet("customers.parquet", target="source")``

``df = read_lakehouse_parquet("incoming/2026/customers.parquet", target="source")``

Derived ``_tsus`` fallback naming:

- ``customers.parquet`` becomes ``customers_tsus.parquet``.
- ``incoming/2026/customers.parquet`` becomes
  ``incoming/2026_tsus/customers.parquet``.

The function does not replace the original file.

The fallback begins after any exception from the original Spark read or
validation action. The current implementation does not first confirm that
the original failure is definitely timestamp-related. It then attempts the
``_tsus`` path. If that path is missing, it performs one single-file
conversion and retries. If both original and fallback reads fail, the
function raises ``RuntimeError``. Underlying Spark, pandas, PyArrow, path,
mount, or conversion errors may appear in verbose output before the final
``RuntimeError``.

The compatibility copy is produced by reading the original Parquet file
with pandas and PyArrow, then rewriting it as a new Parquet file using
microsecond timestamp precision with ``coerce_timestamps="us"`` and
truncated timestamps allowed. The compatibility copy may lose
sub-microsecond timestamp precision because nanosecond timestamps are
coerced to microseconds.

Spark may normally read a Parquet file or compatible dataset path, but the
automatic conversion helper is designed for one local Parquet file. It is
not a distributed folder conversion workflow, and large or multi-file
remediation should be handled as a separate conversion pipeline.

The normal Spark read uses the resolved configured ABFSS path. The
conversion fallback assumes the file is also accessible through the
notebook's default attached Lakehouse mount under
``/lakehouse/default/Files/``. A configured target may resolve correctly
for Spark reading while still being unavailable to the local fallback
mount, in which case fallback conversion can fail.

Compact reader-option example:

``df = read_lakehouse_parquet("incoming/events.parquet", target="source", mergeSchema=True)``

This function does not read a managed Delta table, register Parquet data as
a Lakehouse table, replace or modify the original Parquet file, convert
every file in a Parquet folder, perform a distributed timestamp
conversion, guarantee that the original failure was timestamp-related,
preserve nanosecond precision in the converted copy, delete or refresh an
existing ``_tsus`` copy, register metadata, profile the returned
DataFrame, or automatically cache or persist the returned DataFrame.

[Back to release overview](../index.md)
