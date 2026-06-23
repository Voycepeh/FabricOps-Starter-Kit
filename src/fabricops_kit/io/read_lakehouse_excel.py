"""Owner file for the ``read_lakehouse_excel`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import read_lakehouse_excel_shared


def read_lakehouse_excel(relative_path: str, *, target: str = "source", sheet_name=0, spark_session=None, context: dict[str, Any] | None = None, **read_excel_kwargs):
    """Read an Excel file from a Fabric lakehouse Files path.

    Parameters
    ----------
    relative_path : str
        Excel file path under the lakehouse ``Files`` area.
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

    """
    return read_lakehouse_excel_shared(relative_path, target=target, sheet_name=sheet_name, spark_session=spark_session, context=context, **read_excel_kwargs)
