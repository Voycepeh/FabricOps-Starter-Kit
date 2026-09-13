"""Owner file for the ``read_lakehouse_json`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_json_path, resolve_configured_file_path


def read_lakehouse_json(
    relative_path: str,
    *,
    store: str = "source",
    spark_session=None,
    context: dict[str, Any] | None = None,
    **options,
):
    """Read JSON data from a configured Lakehouse ``Files`` path through Spark.

    FabricOps resolves ``store`` and ``relative_path`` to the configured
    Lakehouse ``Files`` area, then delegates JSON parsing to Spark's native
    JSON reader. Use ``read_lakehouse_table`` instead for managed Delta tables
    in the Lakehouse ``Tables`` area.

    Parameters
    ----------
    relative_path : str
        JSON file or folder path underneath the configured Lakehouse ``Files``
        area. Root-level and nested paths are supported.
    store : str, default="source"
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
    ``df = read_lakehouse_json("incoming/events.json", store="source")``

    ``df = read_lakehouse_json("incoming/events.json", store="source", multiLine=True)``

    This function does not read managed Delta tables, register metadata,
    profile data, convert JSON to Delta, mutate source files, or automatically
    cache or persist the returned DataFrame.

    """
    _store, _relative_path, path = resolve_configured_file_path(store, relative_path, context=context)
    return read_json_path(get_spark_session(spark_session), path, options=options)
