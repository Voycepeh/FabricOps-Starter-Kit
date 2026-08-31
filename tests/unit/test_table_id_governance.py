"""Canonical registered-table governance resolution tests."""

from __future__ import annotations

import pytest
from pathlib import Path

from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.unit


class Frame:
    """Minimal collected-row frame."""

    def __init__(self, rows):
        """Store collected rows."""
        self.rows = rows

    def collect(self):
        """Return stored rows."""
        return self.rows


def catalogue_row(table_id: str, table_name: str, *, active=True, level="table") -> dict:
    """Return one registered Catalogue test row."""
    return {
        "metadata_level": level,
        "table_id": table_id,
        "column_id": None,
        "environment_name": "dev",
        "store_type": "lakehouse",
        "layer": "source",
        "schema_name": "sales",
        "table_name": table_name,
        "load_strategy": "append" if table_id == "table-a" else "overwrite",
        "load_strategy_parameters_json": "{}",
        "is_active": active,
    }


def test_catalogue_resolver_isolates_canonical_table_id(monkeypatch):
    """Resolve A without selecting B's physical identity or processing authoring."""
    rows = [catalogue_row("table-a", "orders"), catalogue_row("table-b", "customers")]
    monkeypatch.setattr(shared, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda *args, **kwargs: Frame(rows))

    identity = shared.resolve_catalogue_table_identity(object(), "dev", "table-a")

    assert identity["table_id"] == "table-a"
    assert identity["table_name"] == "orders"
    assert shared.catalogue_authored_processing(identity)["load_strategy"] == "append"


@pytest.mark.parametrize("table_id", ["", "   "])
def test_catalogue_resolver_rejects_blank_table_id(table_id):
    """Reject blank canonical identities before metadata IO."""
    with pytest.raises(ValueError, match="table_id must be a non-empty"):
        shared.resolve_catalogue_table_identity(object(), "dev", table_id)


def test_catalogue_resolver_rejects_missing_duplicate_and_non_table_rows(monkeypatch):
    """Fail closed for absent, ambiguous, or non-table Catalogue identity rows."""
    monkeypatch.setattr(shared, "configured_lakehouse_schema", lambda *args: None)
    rows = [catalogue_row("table-a", "orders", level="column")]
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda *args, **kwargs: Frame(rows))
    with pytest.raises(ValueError, match="No active registered Catalogue table"):
        shared.resolve_catalogue_table_identity(object(), "dev", "table-a")

    rows[:] = [catalogue_row("table-a", "orders"), catalogue_row("table-a", "orders-copy")]
    with pytest.raises(RuntimeError, match="resolves to 2 active table identities"):
        shared.resolve_catalogue_table_identity(object(), "dev", "table-a")


def test_governed_check_modules_have_no_legacy_table_identity_name():
    """Keep the governed runtime stack on the single canonical identity name."""
    pipeline_root = Path(__file__).parents[2] / "src" / "fabricops_kit" / "pipeline"
    directly_affected = (
        "shared.py",
        "check_schema.py",
        "check_freshness.py",
        "check_changes.py",
        "check_dq.py",
    )
    for name in directly_affected:
        source = (pipeline_root / name).read_text(encoding="utf-8")
        assert "metadata_table_key" not in source
        assert "build_metadata_table_key" not in source
