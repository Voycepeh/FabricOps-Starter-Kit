"""Compatibility facade for Fabric IO public functions and core store types.

The public IO implementations live in one-owner-file modules under
``fabricops_kit.io``. This module remains temporarily so existing imports such
as ``from fabricops_kit.fabric_input_output import read_lakehouse_table`` keep
working while implementation ownership migrates to the IO package.
"""

from __future__ import annotations

from .io import (
    read_lakehouse_csv,
    read_lakehouse_excel,
    read_lakehouse_parquet,
    read_lakehouse_table,
    read_warehouse_query,
    read_warehouse_table,
    write_lakehouse_table,
    write_warehouse_table,
)
from .io_core import FabricStore, _resolve_lakehouse_table_identifier

DEFAULT_ENV = "Sandbox"
DEFAULT_TARGET = "Source"

__all__ = [
    "FabricStore",
    "_resolve_lakehouse_table_identifier",
    "read_lakehouse_csv",
    "read_lakehouse_excel",
    "read_lakehouse_parquet",
    "read_lakehouse_table",
    "read_warehouse_query",
    "read_warehouse_table",
    "write_lakehouse_table",
    "write_warehouse_table",
]
