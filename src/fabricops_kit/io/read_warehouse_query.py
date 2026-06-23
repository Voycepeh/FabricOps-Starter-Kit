"""Owner file for the ``read_warehouse_query`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import read_warehouse_query_shared


def read_warehouse_query(query: str, *, target: str = "warehouse", spark_session=None, context: dict[str, Any] | None = None):
    """Read warehouse rows with SQL pushdown.

    Use this callable when Warehouse data should be filtered or projected by the
    SQL serving engine before Spark receives it. Warehouse reads from Spark use
    the Fabric Warehouse connector path, not native Delta file access. For large
    or repeated PySpark processing, materialize the filtered result into the
    Source Lakehouse as Delta and continue from ``read_lakehouse_table``.

    Rule-of-thumb sizing guidance: small filtered or narrow slices under
    roughly 1 million rows or 1 GB are usually acceptable for ad hoc work;
    1 million to 10 million rows or 1 to 10 GB should be benchmarked first; and
    tables over roughly 10 million rows, over 10 GB, with hundreds of columns,
    or with large text fields should be loaded incrementally into Lakehouse
    Delta before Spark transformations.

    Parameters
    ----------
    query : str
        SQL ``SELECT`` statement, or a CTE beginning with ``WITH`` and ending in
        a ``SELECT``, to execute through the Fabric warehouse connector.
    target : str, default="warehouse"
        Logical warehouse target from ``00_env_config``.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame returned by the SQL serving engine.

    """
    return read_warehouse_query_shared(query, target=target, spark_session=spark_session, context=context)
