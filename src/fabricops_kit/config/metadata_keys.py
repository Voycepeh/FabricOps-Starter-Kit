"""Config-owned stable key helpers for FabricOps metadata records."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _stable_metadata_key(*parts: Any) -> str:
    payload = [
        {"is_null": part is None, "value": None if part is None else str(part).strip().lower()} for part in parts
    ]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def build_metadata_table_key(store_type: Any, layer: Any, schema_name: Any, table_name: Any) -> str:
    """Return the environment-independent logical identity for a table."""
    return _stable_metadata_key(store_type, layer, schema_name, table_name)


def build_metadata_column_key(metadata_table_key: Any, column_name: Any) -> str:
    """Return the environment-independent logical identity for a column."""
    return _stable_metadata_key(metadata_table_key, column_name)


def _build_dq_rule_key(environment_name: Any, dataset_name: Any, table_name: Any, rule_id: Any) -> str:
    normalized = "|".join(
        str(part or "").strip().lower() for part in (environment_name, dataset_name, table_name, rule_id)
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
