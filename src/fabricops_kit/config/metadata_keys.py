"""Private key helpers for FabricOps metadata records."""

from __future__ import annotations

import hashlib
from typing import Any


def _build_dq_rule_key(environment_name: Any, dataset_name: Any, table_name: Any, rule_id: Any) -> str:
    normalized = "|".join(
        str(part or "").strip().lower() for part in (environment_name, dataset_name, table_name, rule_id)
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
