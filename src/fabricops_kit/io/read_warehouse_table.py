"""Owner file for the ``read_warehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import read_warehouse_table_shared


def read_warehouse_table(schema: str, table_name: str, *, target: str = "warehouse", spark_session=None, context: dict[str, Any] | None = None):
    """Read a full table from a Microsoft Fabric warehouse.

    Use this callable for intentional full extracts, such as small reference
    tables or cases where the complete warehouse table is required. Prefer
    ``read_warehouse_query`` when projection or filtering can be pushed down to
    the SQL serving engine.

    Warehouse table reads from Spark use the Fabric Warehouse connector path,
    not native Delta file access. As a rule of thumb, small Warehouse reads are
    usually acceptable for reference or ad hoc work, such as narrow tables,
    filtered slices, or datasets under roughly 1 million rows or 1 GB. For
    1 million to 10 million rows, wide tables, or multi-GB data, benchmark first
    and prefer Lakehouse Delta if the data will be reused. For tens of millions
    of rows, hundreds of columns, large text columns, or tables over roughly
    10 GB, copy or incrementally load the Warehouse data into Lakehouse Delta
    before Spark processing. Avoid a single notebook cell that pulls a very
    large Warehouse table because notebook cells can hit runtime limits.

    Parameters
    ----------
    schema : str
        Warehouse schema name.
    table_name : str
        Warehouse table name.
    target : str, default="warehouse"
        Logical warehouse target from ``00_env_config``.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame loaded through the Fabric warehouse connector.

    """
    return read_warehouse_table_shared(schema, table_name, target=target, spark_session=spark_session, context=context)
