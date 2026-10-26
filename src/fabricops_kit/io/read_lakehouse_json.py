"""Owner file for the ``read_lakehouse_json`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_json_path, resolve_configured_file_path


def read_lakehouse_json(
    relative_path: str,
    *,
    store: str = "Bronze",
    context: dict[str, Any] | None = None,
    **options,
):
    """Read JSON data from a configured Lakehouse ``Files`` path through Spark.

    Spark is resolved automatically from the existing execution session.
    No session is created; Spark-dependent work raises
    ``RuntimeError`` when no session is available.

    FabricOps resolves ``store`` and ``relative_path`` to the configured
    Lakehouse ``Files`` area, then delegates JSON parsing to Spark's native
    JSON reader. Use ``read_lakehouse_table`` instead for managed Delta tables
    in the Lakehouse ``Tables`` area.

    Parameters
    ----------
    relative_path : str
        JSON file or folder path underneath the configured Lakehouse ``Files``
        area. Root-level and nested paths are supported.
    store : str, default="Bronze"
        Logical Lakehouse store key configured by ``00_env_config``.
    context : dict[str, Any], optional
        Active Fabric context override.
    **options
        Options forwarded unchanged to Spark's JSON reader, such as
        ``multiLine``, ``mode``, ``columnNameOfCorruptRecord``, ``dateFormat``,
        ``timestampFormat``, ``encoding``, ``recursiveFileLookup``,
        ``pathGlobFilter``, ``primitivesAsString``, ``allowComments``,
        ``allowSingleQuotes``, and ``allowUnquotedFieldNames``.

    Returns
    -------
    pyspark.sql.DataFrame
        A lazy Spark DataFrame backed by the resolved JSON file or compatible
        files in the supplied folder path.

    Notes
    -----
    Spark normally treats each line as a separate JSON record (JSON Lines or
    newline-delimited JSON). Standard multi-line JSON documents may require
    ``multiLine=True``. Folder paths are passed directly to Spark; FabricOps
    does not iterate through files or eagerly validate or collect the data.

    Examples
    --------
    ``df = read_lakehouse_json("incoming/events.json", store="Bronze")``

    ``df = read_lakehouse_json("incoming/events.json", store="Bronze", multiLine=True)``

    This function does not read managed Delta tables, register metadata,
    profile data, convert JSON to Delta, mutate source files, or automatically
    cache or persist the returned DataFrame.

    """
    spark_session = get_spark_session(context=context)
    _store, _relative_path, path = resolve_configured_file_path(store, relative_path, context=context)
    dataframe = read_json_path(spark_session, path, options=options)
    if not (context or {}).get("_fabricops_suppress_io_log"):
        print(f"Read from → Object: Lakehouse | Store: {store} | Area: Files | Path: {_relative_path}")
    return dataframe
