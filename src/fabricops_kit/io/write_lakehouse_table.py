"""Owner file for the ``write_lakehouse_table`` public IO function."""

from __future__ import annotations

from typing import Any

from .shared import normalize_write_mode, resolve_configured_lakehouse_table, validate_dataframe_writer, write_delta_path


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
    validate_dataframe_writer(df)
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(target, table_name, schema, context=context)
    normalized_mode = normalize_write_mode(mode)
    if repartition_by is not None:
        if isinstance(repartition_by, (list, tuple)):
            df = df.repartition(*repartition_by) if not (repartition_by and isinstance(repartition_by[0], int)) else df.repartition(repartition_by[0], *repartition_by[1:])
        else:
            df = df.repartition(repartition_by)
    if verbose:
        print(f"Writing Lakehouse table to {path}")
    write_delta_path(df, path, mode=normalized_mode, partition_by=partition_by, options=options)
