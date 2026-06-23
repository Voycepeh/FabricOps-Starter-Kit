"""Owner file for the ``read_lakehouse_excel`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_excel_file, resolve_lakehouse_file_location, resolve_target_store


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
    store, _env = resolve_target_store(target, "lakehouse", context=context)
    _relative_path, lakehouse_path = resolve_lakehouse_file_location(store, relative_path)
    return read_excel_file(get_spark_session(spark_session), lakehouse_path, sheet_name=sheet_name, read_excel_kwargs=read_excel_kwargs)
