"""Lower-level Fabric IO implementations shared by package internals.

This module is not a notebook-facing public API. Public IO facades live in
``fabric_input_output``; package internals use this lower layer to avoid public
callable-to-public callable dependencies.
"""

from __future__ import annotations

import re
from typing import Any

from .config import _get_store
from .fabric_input_output import (
    _read_lakehouse_table_core as read_lakehouse_table_core,
    _write_lakehouse_table_core as write_lakehouse_table_core,
)


def configured_lakehouse_schema(config: Any, env: str, target: str) -> str | None:
    """Return the configured schema for a schema-enabled lakehouse target."""
    try:
        store = _get_store(config, env, target)
    except ValueError:
        return None
    if store.kind != "lakehouse" or not getattr(store, "schema_enabled", False):
        return None
    value = str(getattr(store, "schema", "") or "").strip()
    if not value:
        return None
    if any(separator in value for separator in ("/", "\\", ".")):
        raise ValueError("schema must be a simple schema name; do not use paths or dots.")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("schema must contain only letters, numbers, and underscores, and must not start with a number.")
    return value
