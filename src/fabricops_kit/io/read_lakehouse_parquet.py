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
    """Read a Parquet file from a configured Fabric-resolved path through Spark.

    Parameters
    ----------
    relative_path : str
        Parquet file path resolved by the Fabric resolver. Root-level files such
        as ``customers.parquet`` and nested paths such as
        ``input/customers.parquet`` are supported.
    target : str, default="source"
        Logical lakehouse target from ``00_env_config``.
    verbose : bool, default=True
        Whether to print read and timestamp-conversion fallback progress.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.
    **options
        Additional Spark Parquet reader options forwarded to every original and
        timestamp-converted fallback read attempt.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the Parquet path.

    Notes
    -----
    FabricOps resolves the configured Lakehouse Files path from
    ``00_env_config`` and then delegates to Spark's Parquet reader. If Spark
    cannot read the original path because of timestamp precision issues, the
    existing ``_tsus`` fallback conversion path is attempted with the same
    reader options.

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
