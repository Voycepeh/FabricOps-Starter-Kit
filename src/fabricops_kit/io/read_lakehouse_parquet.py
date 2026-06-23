"""Owner file for the ``read_lakehouse_parquet`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import read_lakehouse_parquet_shared


def read_lakehouse_parquet(relative_path: str, *, target: str = "source", verbose: bool = True, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Parquet file from a Fabric lakehouse Files path.

    Parameters
    ----------
    relative_path : str
        Parquet file path under the lakehouse ``Files`` area.
    target : str, default="source"
        Logical lakehouse target from ``00_env_config``.
    verbose : bool, default=True
        Whether to print read and timestamp-conversion fallback progress.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the Parquet path.

    """
    return read_lakehouse_parquet_shared(relative_path, target=target, verbose=verbose, spark_session=spark_session, context=context)
