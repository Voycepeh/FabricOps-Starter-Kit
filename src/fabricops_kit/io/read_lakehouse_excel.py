"""Owner file for the ``read_lakehouse_excel`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_excel_file, resolve_configured_file_path


def read_lakehouse_excel(
    relative_path: str,
    *,
    target: str = "source",
    sheet_name=0,
    spark_session=None,
    context: dict[str, Any] | None = None,
    **read_excel_kwargs,
):
    """Read an Excel workbook from a configured Fabric-resolved path.

    Parameters
    ----------
    relative_path : str
        Excel file path resolved by the Fabric resolver.
    target : str, default="source"
        Logical lakehouse target from ``00_env_config``.
    sheet_name : str or int, default=0
        Worksheet name or index to read.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
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
    DataFrame.

    """
    _store, _relative_path, lakehouse_path = resolve_configured_file_path(target, relative_path, context=context)
    return read_excel_file(
        get_spark_session(spark_session), lakehouse_path, sheet_name=sheet_name, read_excel_kwargs=read_excel_kwargs
    )
