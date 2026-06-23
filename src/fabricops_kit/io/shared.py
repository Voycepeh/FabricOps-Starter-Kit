"""Shared internal IO utilities used by public IO owner files."""

from __future__ import annotations

from typing import Any

from ..io_core import (
    FabricStore,
    _get_spark,
    _lakehouse_file_path,
    _read_csv_path,
    _read_delta_path,
    _read_excel_file,
    _read_warehouse_synapsesql,
    _resolve_lakehouse_file_location,
    _resolve_lakehouse_table_location,
    _resolve_target_store,
    _resolve_warehouse_table_location,
    _validate_dataframe_writer,
    _validate_select_query,
    _write_delta_path,
    _write_warehouse_synapsesql,
    _normalize_write_mode,
    _convert_single_parquet_ns_to_us,
)

DEFAULT_ENV = "Sandbox"
DEFAULT_TARGET = "Source"


def get_spark_session(spark_session=None):
    """Return the explicit or active notebook Spark session."""
    return _get_spark(spark_session)


def resolve_configured_file_path(target: str, relative_path: str, *, context: dict[str, Any] | None = None) -> tuple[FabricStore, str, str]:
    """Resolve a logical target and relative file path through Fabric config."""
    store, _env = _resolve_target_store(target, "lakehouse", context=context)
    normalized_relative_path, path = _resolve_lakehouse_file_location(store, relative_path)
    return store, normalized_relative_path, path


def resolve_configured_lakehouse_table(target: str, table_name: str, schema: str | None, *, context: dict[str, Any] | None = None) -> tuple[FabricStore, str, str | None, str]:
    """Resolve a logical target and table through configured lakehouse metadata."""
    store, _env = _resolve_target_store(target, "lakehouse", context=context)
    table_value, schema_value, path = _resolve_lakehouse_table_location(store, table_name, schema)
    return store, table_value, schema_value, path


def resolve_configured_warehouse_table(target: str, schema: str, table_name: str, *, context: dict[str, Any] | None = None) -> tuple[FabricStore, str, str, str]:
    """Resolve a logical target and table through configured warehouse metadata."""
    store, _env = _resolve_target_store(target, "warehouse", context=context)
    schema_value, table_value, object_name = _resolve_warehouse_table_location(store, schema, table_name)
    return store, schema_value, table_value, object_name


def resolve_configured_warehouse_query_target(target: str, *, context: dict[str, Any] | None = None) -> FabricStore:
    """Resolve a logical target for Fabric warehouse query execution."""
    store, _env = _resolve_target_store(target, "warehouse", context=context)
    return store


def resolve_target_store(target: str, expected_kind: str, *, context: dict[str, Any] | None = None) -> tuple[FabricStore, str]:
    """Resolve and validate a configured Fabric target store."""
    return _resolve_target_store(target, expected_kind, context=context)


def resolve_lakehouse_table_location(store: FabricStore, table_name: str, schema: str | None) -> tuple[str, str | None, str]:
    """Resolve a Lakehouse table to normalized table, schema, and ABFSS path."""
    return _resolve_lakehouse_table_location(store, table_name, schema)


def resolve_lakehouse_file_location(store: FabricStore, relative_path: str) -> tuple[str, str]:
    """Resolve a Lakehouse Files path to normalized relative and ABFSS paths."""
    return _resolve_lakehouse_file_location(store, relative_path)


def resolve_lakehouse_file_path(store: FabricStore, relative_path: str) -> str:
    """Resolve a normalized Lakehouse Files relative path to an ABFSS path."""
    return _lakehouse_file_path(store, relative_path)


def resolve_warehouse_table_location(store: FabricStore, schema: str, table_name: str) -> tuple[str, str, str]:
    """Resolve a Warehouse table to normalized schema, table, and connector target."""
    return _resolve_warehouse_table_location(store, schema, table_name)


def normalize_write_mode(mode: str) -> str:
    """Return a supported Spark write mode."""
    return _normalize_write_mode(mode)


def validate_dataframe_writer(df) -> None:
    """Validate that an object exposes the Spark DataFrame write contract."""
    _validate_dataframe_writer(df)


def validate_select_query(query: str) -> str:
    """Validate and normalize SQL suitable for Warehouse pushdown."""
    return _validate_select_query(query)


def read_delta_path(spark_obj, path: str):
    """Read a Delta path through Spark."""
    return _read_delta_path(spark_obj, path)


def read_csv_path(spark_obj, path: str, *, header: bool, options: dict[str, Any]):
    """Read a CSV path through Spark."""
    return _read_csv_path(spark_obj, path, header=header, options=options)


def write_delta_path(df, path: str, *, mode: str, partition_by=None, options: dict[str, Any] | None = None) -> None:
    """Write a DataFrame to a Delta path through Spark."""
    _write_delta_path(df, path, mode=mode, partition_by=partition_by, options=options)


def read_warehouse_synapsesql(spark_obj, store: FabricStore, synapsesql_target: str):
    """Read from Fabric Warehouse through the Spark connector."""
    return _read_warehouse_synapsesql(spark_obj, store, synapsesql_target)


def write_warehouse_synapsesql(df, store: FabricStore, synapsesql_target: str, *, mode: str) -> None:
    """Write to Fabric Warehouse through the Spark connector."""
    _write_warehouse_synapsesql(df, store, synapsesql_target, mode=mode)


def read_excel_file(spark_obj, lakehouse_path: str, *, sheet_name, read_excel_kwargs: dict[str, Any]):
    """Read Excel binary content from Lakehouse Files and return a Spark DataFrame."""
    return _read_excel_file(spark_obj, lakehouse_path, sheet_name=sheet_name, read_excel_kwargs=read_excel_kwargs)


def convert_single_parquet_ns_to_us(local_in_path, local_out_path, verbose=True):
    """Convert one local Parquet file from nanosecond to microsecond timestamps."""
    _convert_single_parquet_ns_to_us(local_in_path, local_out_path, verbose=verbose)
