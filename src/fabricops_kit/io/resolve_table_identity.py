"""Internal owner for normalized configured table identities."""

from .shared import resolve_lakehouse_table_location, resolve_warehouse_table_location

__all__ = ["resolve_lakehouse_table_location", "resolve_warehouse_table_location"]
