"""Owner file for the ``read_lakehouse_excel`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_excel_file, resolve_configured_file_path


def read_lakehouse_excel(
    relative_path: str,
    *,
    store: str = "Bronze",
    sheet_name=0,
    context: dict[str, Any] | None = None,
    **read_excel_kwargs,
):
    """Read an Excel workbook from a configured Fabric-resolved path.

    Spark is resolved automatically from the existing execution session.
    No session is created; Spark-dependent work raises
    ``RuntimeError`` when no session is available.

    Parameters
    ----------
    relative_path : str
        Excel file path resolved by the Fabric resolver.
    store : str, default="Bronze"
        Logical Lakehouse store key from ``00_env_config``.
    sheet_name : str or int, default=0
        Worksheet name or index to read.
    context : dict[str, Any], optional
        Active Fabric context override.
    **read_excel_kwargs
        Additional keyword arguments passed to ``pandas.read_excel``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame converted from the selected Excel worksheet.

    Notes
    -----
    FabricOps resolves the configured Lakehouse Files path from
    ``00_env_config``, reads the workbook binary through Spark, parses it with
    ``pandas.read_excel``, and converts the pandas DataFrame back to a Spark
    DataFrame. The temporary local workbook is deleted after parsing, including
    when parsing raises an error.

    """
    spark_session = get_spark_session(context=context)
    _store, _relative_path, lakehouse_path = resolve_configured_file_path(store, relative_path, context=context)
    dataframe = read_excel_file(
        spark_session, lakehouse_path, sheet_name=sheet_name, read_excel_kwargs=read_excel_kwargs
    )
    if not (context or {}).get("_fabricops_suppress_io_log"):
        print(f"Read from → Object: Lakehouse | Store: {store} | Area: Files | Path: {_relative_path}")
    return dataframe
