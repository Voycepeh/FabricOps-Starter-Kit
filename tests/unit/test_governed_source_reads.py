"""Focused tests for governed physical source-read scopes."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
import importlib

import pytest

from fabricops_kit.config import FabricStore
from fabricops_kit.io.shared import build_warehouse_scoped_query, validate_processing_scope


@pytest.mark.parametrize(
    ("scope", "message"),
    [
        ({"type": "watermark", "lower_bound": 1, "upper_bound": 2}, "requires column"),
        ({"type": "watermark", "column": "id", "upper_bound": 2}, "lower_bound"),
        ({"type": "watermark", "column": "id", "lower_bound": 1}, "upper_bound"),
        ({"type": "partition", "values": [1]}, "requires column"),
        ({"type": "partition", "column": "bucket", "values": []}, "non-empty values"),
        ({"type": "mystery"}, "type must be one of"),
    ],
)
def test_processing_scope_rejects_malformed_states(scope, message):
    """Malformed physical-read scopes fail before any source read."""
    with pytest.raises(ValueError, match=message):
        validate_processing_scope(scope)


def test_warehouse_scope_queries_encode_supported_values_and_identifiers():
    """Warehouse scopes produce bounded and safely escaped SQL predicates."""
    watermark = build_warehouse_scoped_query(
        "dbo",
        "Bookings",
        {
            "type": "watermark",
            "column": "modified_datetime",
            "lower_bound": datetime(2026, 8, 25, 10, 30),
            "upper_bound": datetime(2026, 8, 26, 10, 30),
        },
    )
    assert watermark == (
        "SELECT * FROM [dbo].[Bookings] WHERE [modified_datetime] > '2026-08-25 10:30:00' "
        "AND [modified_datetime] <= '2026-08-26 10:30:00'"
    )
    partition = build_warehouse_scoped_query(
        "dbo",
        "StudentSnapshot",
        {"type": "partition", "column": "bucket", "values": [date(2026, 8, 26), "O'Brien", 7, Decimal("8.5")]},
    )
    assert partition == (
        "SELECT * FROM [dbo].[StudentSnapshot] WHERE [bucket] IN "
        "('2026-08-26', 'O''Brien', 7, 8.5)"
    )
    with pytest.raises(ValueError, match="simple identifier"):
        build_warehouse_scoped_query(
            "dbo", "Bookings", {"type": "watermark", "column": "id] OR 1=1", "lower_bound": 1, "upper_bound": 2}
        )


def test_lakehouse_reader_preserves_full_paths_and_skips_without_read(monkeypatch):
    """Lakehouse full scopes reuse the read path while skip performs no IO."""
    owner = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    calls = []
    monkeypatch.setattr(
        owner,
        "resolve_configured_lakehouse_table",
        lambda *args, **kwargs: calls.append("resolve") or (object(), "orders", None, "resolved://orders"),
    )
    monkeypatch.setattr(owner, "get_spark_session", lambda spark: spark)
    monkeypatch.setattr(
        owner, "read_delta_path", lambda spark, path, *, options=None: calls.append((path, options)) or "frame"
    )
    monkeypatch.setattr(
        owner,
        "apply_lakehouse_processing_scope",
        lambda frame, scope: calls.append(scope) or frame,
    )

    assert owner.read_lakehouse_table("orders", spark_session=object()) == "frame"
    assert owner.read_lakehouse_table(
        "orders", spark_session=object(), processing_scope={"type": "full_dataset"}
    ) == "frame"
    with pytest.raises(ValueError, match="resolved to skip"):
        owner.read_lakehouse_table("orders", spark_session=object(), processing_scope={"type": "skip"})
    assert calls.count("resolve") == 2


def test_warehouse_incremental_scopes_use_query_path_and_skip_without_read(monkeypatch):
    """Warehouse incremental scopes push predicates down instead of reading the named table."""
    owner = importlib.import_module("fabricops_kit.io.read_warehouse_table")
    store = FabricStore(env="dev", workspace_id="w", item_id="i", name="warehouse", kind="warehouse")
    calls = []
    monkeypatch.setattr(
        owner,
        "resolve_configured_warehouse_table",
        lambda *args, **kwargs: calls.append("resolve") or (store, "dbo", "Bookings", "warehouse.dbo.Bookings"),
    )
    monkeypatch.setattr(owner, "get_spark_session", lambda spark: spark)
    monkeypatch.setattr(
        owner,
        "read_warehouse_synapsesql",
        lambda spark, store, target, *, options=None: calls.append(target) or target,
    )

    assert owner.read_warehouse_table("dbo", "Bookings", spark_session=object()) == "warehouse.dbo.Bookings"
    assert owner.read_warehouse_table(
        "dbo", "Bookings", spark_session=object(), processing_scope={"type": "full_dataset"}
    ) == "warehouse.dbo.Bookings"
    query = owner.read_warehouse_table(
        "dbo",
        "Bookings",
        spark_session=object(),
        processing_scope={"type": "watermark", "column": "id", "lower_bound": 10, "upper_bound": 20},
    )
    assert query.endswith("WHERE [id] > 10 AND [id] <= 20")
    assert query != "warehouse.dbo.Bookings"
    with pytest.raises(ValueError, match="resolved to skip"):
        owner.read_warehouse_table(
            "dbo", "Bookings", spark_session=object(), processing_scope={"type": "skip"}
        )
    assert calls.count("resolve") == 3
