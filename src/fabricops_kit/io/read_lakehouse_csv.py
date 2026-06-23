"""Owner file for the ``read_lakehouse_csv`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_csv_path, resolve_configured_file_path


def read_lakehouse_csv(relative_path: str, *, target: str = "source", spark_session=None, header: bool = True, context: dict[str, Any] | None = None, **options):
    """Read a CSV file from a configured Fabric-resolved path.

    Parameters
    ----------
    relative_path : str
        CSV file or folder path resolved by the Fabric resolver.
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
    _store, _relative_path, path = resolve_configured_file_path(target, relative_path, context=context)
    return read_csv_path(get_spark_session(spark_session), path, header=header, options=options)
