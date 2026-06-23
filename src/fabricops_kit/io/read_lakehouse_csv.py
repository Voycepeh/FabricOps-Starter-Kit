"""Owner file for the ``read_lakehouse_csv`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import read_lakehouse_csv_shared


def read_lakehouse_csv(relative_path: str, *, target: str = "source", spark_session=None, header: bool = True, context: dict[str, Any] | None = None, **options):
    """Read a CSV file from a Fabric lakehouse Files path.

    Parameters
    ----------
    relative_path : str
        CSV file or folder path under the lakehouse ``Files`` area.
    target : str, default="source"
        Logical lakehouse target from ``00_env_config``.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    header : bool, default=True
        Whether the first row contains column names.
    context : dict[str, Any], optional
        Active Fabric context override.
    **options
        Additional Spark CSV reader options.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the CSV path.

    """
    return read_lakehouse_csv_shared(relative_path, target=target, spark_session=spark_session, header=header, context=context, **options)
