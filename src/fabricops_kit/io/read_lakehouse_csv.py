"""Owner file for the ``read_lakehouse_csv`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_csv_path, resolve_configured_file_path


def read_lakehouse_csv(
    relative_path: str,
    *,
    target: str = "source",
    spark_session=None,
    header: bool = True,
    context: dict[str, Any] | None = None,
    **options,
):
    """Resolve CSV data in a Lakehouse Files path and return a lazy Spark DataFrame.

    Use ``read_lakehouse_csv`` for CSV data stored under the Lakehouse
    ``Files`` area. Use ``read_lakehouse_table`` for managed Delta tables
    stored under the Lakehouse ``Tables`` area.

    This function reads from the Lakehouse ``Files`` area, not a managed Delta
    table in the ``Tables`` area. It can resolve either a single CSV file path
    or a folder path, applies the ``header`` setting, forwards all additional
    CSV reader options directly to Spark, and returns a lazy Spark DataFrame.
    The resolved location is conceptually
    ``<configured lakehouse>/Files/<relative_path>``, which FabricOps maps to
    the corresponding ABFSS path before delegating to Spark.

    Parameters
    ----------
    relative_path : str
        Relative CSV file or folder path resolved underneath the configured
        Lakehouse ``Files`` area.
    target : str, default="source"
        Logical Lakehouse target from ``00_env_config``. It is not necessarily
        the literal physical Lakehouse name.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
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

    Returns
    -------
    pyspark.sql.DataFrame
        A lazy Spark DataFrame representing the CSV file or compatible CSV
        files found at the resolved Lakehouse ``Files`` path. Column types
        follow Spark CSV reader behavior and generally remain strings unless
        schema inference or other schema handling is explicitly requested.

    Notes
    -----
    FabricOps resolves the configured Lakehouse Files path from
    ``00_env_config`` and then delegates to Spark's CSV reader with the supplied
    options. Calling this function constructs a Spark read plan, and the file
    scan occurs when a downstream action executes, such as ``display``,
    ``count``, ``collect``, or a DataFrame write. The function does not
    immediately load the complete file into notebook memory.

    Compact examples:

    ``df = read_lakehouse_csv("incoming/customers.csv", target="source")``

    ``df = read_lakehouse_csv("incoming/customers/", target="source")``

    ``df = read_lakehouse_csv("incoming/customers.csv", target="source", inferSchema=True)``

    ``df = read_lakehouse_csv("incoming/orders.csv", target="source", header=True, inferSchema=True, sep=",", encoding="UTF-8", mode="PERMISSIVE")``

    When a folder path is supplied, Spark reads compatible CSV files from that
    path into one DataFrame according to Spark CSV reader behavior. FabricOps
    does not manually loop through or append files.

    The function sets the ``header`` option and forwards the caller's CSV
    options. It does not automatically infer data types. Unless the caller
    requests schema inference or another schema strategy, Spark CSV columns are
    generally read as strings. ``inferSchema=True`` can be passed through
    ``**options`` when inference is desired.

    This function does not convert CSV data into a Delta table, write, move,
    rename, or delete source files, register metadata, profile the returned
    DataFrame, remove duplicate rows, standardize column names, infer schema
    unless requested through Spark options, validate that every CSV file in a
    folder has identical structure, apply custom malformed-record handling
    beyond the supplied Spark CSV options, or automatically cache or persist
    the returned DataFrame.

    """
    _store, _relative_path, path = resolve_configured_file_path(target, relative_path, context=context)
    return read_csv_path(get_spark_session(spark_session), path, header=header, options=options)
