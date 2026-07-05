"""Owner file for the ``read_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import get_spark_session, read_delta_path, resolve_configured_lakehouse_table


def read_lakehouse_table(
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
    spark_session=None,
    context: dict[str, Any] | None = None,
    **options,
):
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
    **options
        Additional Spark Delta reader options forwarded to ``DataFrameReader``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded from the configured Delta table path.

    Notes
    -----
    FabricOps resolves the configured Lakehouse Tables path from
    ``00_env_config`` and then delegates to Spark's Delta reader with any
    supplied reader options.

    """
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        target, table_name, schema, context=context
    )
    return read_delta_path(get_spark_session(spark_session), path, options=options)
