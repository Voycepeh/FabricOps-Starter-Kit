"""Stable logical identity helpers for the staged metadata model."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _stable_metadata_id(*parts: Any) -> str:
    """Return a deterministic SHA-256 identity from normalized logical parts."""
    payload = [
        {"is_null": part is None, "value": None if part is None else str(part).strip().lower()}
        for part in parts
    ]
    return hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def build_table_id(store_type: Any, layer: Any, schema_name: Any, table_name: Any) -> str:
    """Return the environment-independent logical identity for a table asset."""
    return _stable_metadata_id(store_type, layer, schema_name, table_name)


def build_column_id(table_id: Any, column_name: Any) -> str:
    """Return the environment-independent logical identity for a column asset."""
    return _stable_metadata_id(table_id, column_name)


__all__ = ["build_column_id", "build_table_id"]
