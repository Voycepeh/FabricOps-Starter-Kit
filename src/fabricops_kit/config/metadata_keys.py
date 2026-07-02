"""Config-owned stable key helpers for FabricOps metadata records."""

from __future__ import annotations

import hashlib
from typing import Any


def _stable_metadata_key(*parts: Any) -> str:
    normalized = "|".join(str(part or "").strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _build_metadata_table_key(environment_name: Any, dataset_name: Any, table_name: Any) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name)


def _build_metadata_column_key(environment_name: Any, dataset_name: Any, table_name: Any, column_name: Any) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name, column_name)


def _build_dq_rule_key(environment_name: Any, dataset_name: Any, table_name: Any, rule_id: Any) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name, rule_id)
