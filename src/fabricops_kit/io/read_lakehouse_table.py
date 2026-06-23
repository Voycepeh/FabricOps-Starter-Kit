"""Owner file for the ``read_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import read_lakehouse_table_shared


def read_lakehouse_table(table_name: str, *, target: str = "source", schema: str | None = None, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Delta table from a Fabric lakehouse.

    Lakehouse Delta is the preferred source for repeated PySpark
    transformations in FabricOps. When source data starts in a Fabric Warehouse,
    materialize large or repeatedly used data into the Source Lakehouse as Delta
    first, then read it with this callable.

    Parameters
    ----------
    table_name : str
        Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name.
    target : str, default="source"
        Logical lakehouse target from ``00_env_config``.
    schema : str or None, default=None
        Optional schema override for schema-enabled lakehouses.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the configured Delta table path.

    """
    return read_lakehouse_table_shared(table_name, target=target, schema=schema, spark_session=spark_session, context=context)
