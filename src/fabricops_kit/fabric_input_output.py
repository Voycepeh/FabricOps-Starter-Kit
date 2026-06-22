"""Fabric path and IO helpers for explicit lakehouse and warehouse routing."""

from __future__ import annotations

from typing import Any

from .io_core import (
    FabricStore,
    _resolve_lakehouse_table_identifier,
    read_lakehouse_csv_core,
    read_lakehouse_excel_core,
    read_lakehouse_parquet_core,
    read_lakehouse_table_core,
    read_warehouse_query_core,
    read_warehouse_table_core,
    write_lakehouse_table_core,
    write_warehouse_table_core,
)

DEFAULT_ENV = "Sandbox"
DEFAULT_TARGET = "Source"


def read_lakehouse_table(table_name: str, *, target: str = "source", schema: str | None = None, spark_session=None, context: dict[str, Any] | None = None):
    """Read a Delta table from a Fabric lakehouse.

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
    return read_lakehouse_table_core(table_name, target=target, schema=schema, spark_session=spark_session, context=context)


def write_lakehouse_table(df, table_name: str, *, target: str = "unified", schema=None, mode="append", partition_by=None, repartition_by=None, options=None, verbose=True, context=None):
    """Write a Spark DataFrame to a Fabric lakehouse Delta table.

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
    return write_lakehouse_table_core(df, table_name, target=target, schema=schema, mode=mode, partition_by=partition_by, repartition_by=repartition_by, options=options, verbose=verbose, context=context)


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
    return read_lakehouse_csv_core(relative_path, target=target, spark_session=spark_session, header=header, context=context, **options)


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
    return read_lakehouse_parquet_core(relative_path, target=target, verbose=verbose, spark_session=spark_session, context=context)


def read_lakehouse_excel(relative_path: str, *, target: str = "source", sheet_name=0, spark_session=None, context: dict[str, Any] | None = None, **read_excel_kwargs):
    """Read an Excel file from a Fabric lakehouse Files path.

    Parameters
    ----------
    relative_path : str
        Excel file path under the lakehouse ``Files`` area.
    target : str, default="source"
        Logical lakehouse target from ``00_env_config``.
    sheet_name : str or int, default=0
        Worksheet name or index to read.
    spark_session : object, optional
        Spark session to use instead of the notebook global ``spark``.
    context : dict[str, Any], optional
        Active Fabric context override.
    **read_excel_kwargs
        Additional keyword arguments passed to ``pandas.read_excel``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame converted from the selected Excel worksheet.
    """
    return read_lakehouse_excel_core(relative_path, target=target, sheet_name=sheet_name, spark_session=spark_session, context=context, **read_excel_kwargs)


def read_warehouse_table(schema: str, table_name: str, *, target: str = "warehouse", spark_session=None, context: dict[str, Any] | None = None):
    """Read a full table from a Microsoft Fabric warehouse.

    Use this callable for intentional full extracts, such as small reference
    tables or cases where the complete warehouse table is required. Prefer
    ``read_warehouse_query`` when projection or filtering can be pushed down to
    the SQL serving engine.

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
    return read_warehouse_table_core(schema, table_name, target=target, spark_session=spark_session, context=context)


def read_warehouse_query(query: str, *, target: str = "warehouse", spark_session=None, context: dict[str, Any] | None = None):
    """Read warehouse rows with SQL pushdown.

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
    return read_warehouse_query_core(query, target=target, spark_session=spark_session, context=context)


def write_warehouse_table(df, schema: str, table_name: str, *, target: str = "warehouse", mode: str = "append", context: dict[str, Any] | None = None):
    """Write a Spark DataFrame to a Microsoft Fabric warehouse table.

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
    return write_warehouse_table_core(df, schema, table_name, target=target, mode=mode, context=context)
