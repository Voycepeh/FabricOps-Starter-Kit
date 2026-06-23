"""Owner file for the ``write_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import write_lakehouse_table_shared


def write_lakehouse_table(df, table_name: str, *, target: str = "unified", schema=None, mode="append", partition_by=None, repartition_by=None, options=None, verbose=True, context=None):
    """Write a Spark DataFrame to a Fabric lakehouse Delta table.

    Lakehouse Delta is optimized for FabricOps PySpark processing and reuse.
    Prefer this callable for intermediate, Unified, Product, and metadata Delta
    outputs that will be read repeatedly by Spark. Publish selected serving
    outputs to Warehouse separately when SQL serving is required.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to write.
    table_name : str
        Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name.
    target : str, default="unified"
        Logical lakehouse target from ``00_env_config``.
    schema : str or None, default=None
        Optional schema override for schema-enabled lakehouses.
    mode : str, default="append"
        Spark write mode: ``append``, ``overwrite``, ``errorifexists``, or ``ignore``.
    partition_by : str or list[str], optional
        Column or columns used to physically partition the Delta table.
    repartition_by : int, str, list, or tuple, optional
        Optional repartitioning before write.
    options : dict, optional
        Additional Spark DataFrameWriter options.
    verbose : bool, default=True
        Whether to print the resolved output path before writing.
    context : dict[str, Any], optional
        Active Fabric context override.

    Returns
    -------
    None
        The DataFrame is written to the configured Delta table path.

    """
    return write_lakehouse_table_shared(df, table_name, target=target, schema=schema, mode=mode, partition_by=partition_by, repartition_by=repartition_by, options=options, verbose=verbose, context=context)
