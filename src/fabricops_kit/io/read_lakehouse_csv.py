"""Owner file for the ``read_lakehouse_csv`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_csv_path, resolve_configured_file_path


def read_lakehouse_csv(
    relative_path: str,
    *,
    store: str = "Bronze",
    header: bool = True,
    context: dict[str, Any] | None = None,
    **options,
):
    """Read CSV files from a configured Lakehouse Files location.

    Spark is resolved automatically from the existing execution session.
    No session is created; Spark-dependent work raises
    ``RuntimeError`` when no session is available.

    Use for a file, folder, or wildcard path. Columns remain strings unless
    Spark schema inference or another schema strategy is requested.

    Parameters
    ----------
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

    Returns
    -------
    pyspark.sql.DataFrame
        A lazy Spark DataFrame representing the CSV file or compatible CSV
        files found at the resolved Lakehouse ``Files`` path. Column types
        follow Spark CSV reader behavior and generally remain strings unless
        schema inference or other schema handling is explicitly requested.

    Notes
    -----
    The Spark DataFrame is lazy; downstream actions evaluate the read. Additional
    reader options are forwarded to Spark. Folder compatibility and malformed
    record handling follow Spark CSV options.

    Examples
    --------
    >>> orders_df = read_lakehouse_csv("incoming/orders.csv", inferSchema=True)

    """
    spark_session = get_spark_session(context=context)
    _store, _relative_path, path = resolve_configured_file_path(store, relative_path, context=context)
    dataframe = read_csv_path(spark_session, path, header=header, options=options)
    if not (context or {}).get("_fabricops_suppress_io_log"):
        print(f"Read from → Object: Lakehouse | Store: {store} | Area: Files | Path: {_relative_path}")
    return dataframe
