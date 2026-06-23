"""Owner file for the ``read_lakehouse_excel`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_path, get_spark_session, read_excel_file


def read_lakehouse_excel(relative_path: str, *, target: str = "source", sheet_name=0, spark_session=None, context: dict[str, Any] | None = None, **read_excel_kwargs):
    """Read an Excel workbook from a Fabric resolved path.

    Parameters
    ----------
    relative_path : str
        Relative workbook path resolved through ``get_path``.
    target : str, default="source"
        Logical target from ``00_env_config``.
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
    Path construction is delegated to ``get_path``. The workbook is read from
    the resolved Fabric path with Excel parsing dependencies and converted to
    a Spark DataFrame. Validate headers and inferred types before using the
    result as pipeline input.
    """
    path = get_path(relative_path, target=target, context=context)
    return read_excel_file(get_spark_session(spark_session), path, sheet_name=sheet_name, read_excel_kwargs=read_excel_kwargs)
