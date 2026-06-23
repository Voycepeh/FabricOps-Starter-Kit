"""Shared internal IO implementations for public owner files."""

from __future__ import annotations

from typing import Any

from ..io_core import (
    FabricStore,
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


def read_lakehouse_table_shared(
    table_name: str,
    *,
    target: str,
    schema: str | None = None,
    spark_session=None,
    context: dict[str, Any] | None = None,
):
    """Read a Lakehouse Delta table for the public owner file."""
    return read_lakehouse_table_core(
        table_name,
        target=target,
        schema=schema,
        spark_session=spark_session,
        context=context,
    )


def write_lakehouse_table_shared(
    df,
    table_name: str,
    *,
    target: str,
    schema: str | None,
    mode: str,
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose: bool = True,
    context=None,
):
    """Write a Lakehouse Delta table for the public owner file."""
    return write_lakehouse_table_core(
        df,
        table_name,
        target=target,
        schema=schema,
        mode=mode,
        partition_by=partition_by,
        repartition_by=repartition_by,
        options=options,
        verbose=verbose,
        context=context,
    )


def read_lakehouse_csv_shared(
    relative_path: str,
    *,
    target: str,
    spark_session=None,
    header: bool = True,
    context: dict[str, Any] | None = None,
    **options,
):
    """Read Lakehouse CSV files for the public owner file."""
    return read_lakehouse_csv_core(
        relative_path,
        target=target,
        spark_session=spark_session,
        header=header,
        context=context,
        **options,
    )


def read_lakehouse_parquet_shared(
    relative_path: str,
    *,
    target: str,
    verbose: bool = True,
    spark_session=None,
    context: dict[str, Any] | None = None,
):
    """Read Lakehouse Parquet files for the public owner file."""
    return read_lakehouse_parquet_core(
        relative_path,
        target=target,
        verbose=verbose,
        spark_session=spark_session,
        context=context,
    )


def read_lakehouse_excel_shared(
    relative_path: str,
    *,
    target: str,
    sheet_name=0,
    spark_session=None,
    context: dict[str, Any] | None = None,
    **read_excel_kwargs,
):
    """Read Lakehouse Excel files for the public owner file."""
    return read_lakehouse_excel_core(
        relative_path,
        target=target,
        sheet_name=sheet_name,
        spark_session=spark_session,
        context=context,
        **read_excel_kwargs,
    )


def read_warehouse_table_shared(
    schema: str,
    table_name: str,
    *,
    target: str,
    spark_session=None,
    context: dict[str, Any] | None = None,
):
    """Read a Warehouse table for the public owner file."""
    return read_warehouse_table_core(
        schema,
        table_name,
        target=target,
        spark_session=spark_session,
        context=context,
    )


def read_warehouse_query_shared(
    query: str,
    *,
    target: str,
    spark_session=None,
    context: dict[str, Any] | None = None,
):
    """Read a Warehouse SQL query for the public owner file."""
    return read_warehouse_query_core(
        query,
        target=target,
        spark_session=spark_session,
        context=context,
    )


def write_warehouse_table_shared(
    df,
    schema: str,
    table_name: str,
    *,
    target: str,
    mode: str,
    context: dict[str, Any] | None = None,
):
    """Write a Warehouse table for the public owner file."""
    return write_warehouse_table_core(
        df,
        schema,
        table_name,
        target=target,
        mode=mode,
        context=context,
    )
