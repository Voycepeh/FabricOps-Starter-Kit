"""Owner file for the ``read_lakehouse_parquet`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import (
    convert_single_parquet_ns_to_us,
    get_spark_session,
    resolve_configured_file_path,
    resolve_lakehouse_file_path,
)


def read_lakehouse_parquet(
    relative_path: str,
    *,
    target: str = "source",
    verbose: bool = True,
    spark_session=None,
    context: dict[str, Any] | None = None,
    **options,
):
    """Read Parquet data from the configured Lakehouse ``Files`` area through Spark.

    Use ``read_lakehouse_parquet`` for Parquet files stored under the
    Lakehouse ``Files`` area. Use ``read_lakehouse_table`` for managed Delta
    tables stored under the Lakehouse ``Tables`` area.

    This function reads from the Lakehouse ``Files`` area, not a managed Delta
    table in the ``Tables`` area. FabricOps resolves the logical target and
    relative path through configuration, attempts a normal Spark Parquet read
    first, forces a small Spark action to verify that the data can actually be
    decoded, falls back to a derived ``_tsus`` path when the original read
    fails, may create a converted Parquet copy with microsecond timestamp
    precision when the fallback path is missing, and returns a Spark DataFrame
    backed by either the original path or the fallback path.

    Parameters
    ----------
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

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame backed by either the original resolved Parquet path
        or the compatible ``_tsus`` fallback path. Before returning, the
        function executes a one-row Spark action to verify that the selected
        data can be decoded.

    Raises
    ------
    RuntimeError
        When neither the original path nor the ``_tsus`` fallback path can be
        read successfully.

    Notes
    -----
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

    """
    store, normalized_relative_path, orig_spark_path = resolve_configured_file_path(
        target, relative_path, context=context
    )
    spark_obj = get_spark_session(spark_session)
    parts = normalized_relative_path.split("/")
    if len(parts) == 1:
        stem, dot, suffix = parts[0].rpartition(".")
        tsus_relative_path = f"{stem}_tsus{dot}{suffix}" if dot else f"{parts[0]}_tsus"
        tsus_dir: list[str] = []
    else:
        tsus_dir = parts[:-2] + [parts[-2] + "_tsus"]
        tsus_relative_path = "/".join(tsus_dir + [parts[-1]])
    tsus_spark_path = resolve_lakehouse_file_path(store, tsus_relative_path)
    orig_local_path = f"/lakehouse/default/Files/{normalized_relative_path}"
    tsus_local_path = f"/lakehouse/default/Files/{tsus_relative_path}"
    if verbose:
        print(f"Try Spark read: {orig_spark_path}")
    try:
        reader = spark_obj.read
        for key, value in options.items():
            reader = reader.option(key, value)
        df = reader.parquet(orig_spark_path)
        _ = df.limit(1).collect()
        if verbose:
            print("SUCCESS: Spark read original path.")
        return df
    except Exception as exc:
        if verbose:
            print(f"Original Parquet read failed. Will try fallback path. Exception: {exc}")
    for try_convert in range(2):
        if verbose:
            print(f"Try Spark read: {tsus_spark_path}{' after single-file convert' if try_convert else ''}")
        try:
            reader = spark_obj.read
            for key, value in options.items():
                reader = reader.option(key, value)
            df = reader.parquet(tsus_spark_path)
            _ = df.limit(1).collect()
            if verbose:
                print("SUCCESS: Spark read _tsus path.")
            return df
        except Exception as exc:
            msg = str(exc)
            path_not_found = (
                "[PATH_NOT_FOUND]" in msg or "Path does not exist" in msg or "No such file or directory" in msg
            )
            if try_convert == 0 and path_not_found:
                if verbose:
                    print("PATH NOT FOUND for _tsus parquet. Will convert one file and retry.")
                try:
                    if tsus_dir:
                        mssparkutils.fs.mkdirs(resolve_lakehouse_file_path(store, "/".join(tsus_dir)))
                except Exception:
                    pass
                convert_single_parquet_ns_to_us(
                    local_in_path=orig_local_path, local_out_path=tsus_local_path, verbose=verbose
                )
            else:
                if verbose:
                    print(f"FAILED: Spark read _tsus path. Exception: {exc}")
                break
    raise RuntimeError("Failed to read from both original and _tsus Parquet paths.")
