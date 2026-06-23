"""Owner file for the ``write_warehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import write_warehouse_table_shared


def write_warehouse_table(df, schema: str, table_name: str, *, target: str = "warehouse", mode: str = "append", context: dict[str, Any] | None = None):
    """Write a Spark DataFrame to a Microsoft Fabric warehouse table.

    Use this callable for final serving publication when Warehouse SQL access is
    needed. Keep repeated PySpark transformations in Lakehouse Delta first, then
    publish curated, appropriately sized outputs to Warehouse. Warehouse writes
    use the Fabric connector path rather than native Delta file writes, so
    benchmark wide or multi-GB publications and consider publishing smaller
    serving tables when possible.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to publish.
    schema : str
        Warehouse schema name.
    table_name : str
        Warehouse table name.
    target : str, default="warehouse"
        Logical warehouse target from ``00_env_config``.
    mode : str, default="append"
        Spark writer mode supported by the Fabric connector.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    None
        The DataFrame is written through the Fabric warehouse connector.

    """
    return write_warehouse_table_shared(df, schema, table_name, target=target, mode=mode, context=context)
