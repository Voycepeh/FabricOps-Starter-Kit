"""Tests for governed target load execution boundaries."""
# ruff: noqa: D103

from __future__ import annotations

import pytest

from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.unit


def _capture_writes(monkeypatch):
    calls = []
    monkeypatch.setattr(shared, "write_lakehouse_table_core", lambda *args, **kwargs: calls.append((args, kwargs)))
    return calls


def test_full_overwrite_uses_full_table_overwrite(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared._apply_load_strategy(
        object(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "overwrite"}, scope={"read_strategy": "full"},
    )
    assert calls[0][1]["mode"] == "overwrite"
    assert "options" not in calls[0][1]


def test_incremental_overwrite_uses_replace_where(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared._apply_load_strategy(
        object(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "overwrite", "partition_column": "business_date"},
        scope={
            "read_strategy": "incremental", "partition_column": "business_date",
            "partition_values": ["2026-08-21"],
        },
    )
    assert calls[0][1]["mode"] == "overwrite"
    assert calls[0][1]["options"] == {"replaceWhere": "`business_date` IN ('2026-08-21')"}


def test_incremental_overwrite_rejects_unsafe_partition_configuration(monkeypatch):
    calls = _capture_writes(monkeypatch)
    with pytest.raises(ValueError, match="matching safe target partition"):
        shared._apply_load_strategy(
            object(), table_name="students", target="unified", schema="dbo",
            processing={"load_strategy": "overwrite", "partition_column": "other_date"},
            scope={
                "read_strategy": "incremental", "partition_column": "business_date",
                "partition_values": ["2026-08-21"],
            },
        )
    assert calls == []


def test_append_uses_low_level_append_only_after_scope_resolution(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared._apply_load_strategy(
        object(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "append"},
        scope={"read_strategy": "incremental", "partition_values": ["2026-08-21"]},
    )
    assert calls[0][1]["mode"] == "append"


def test_incremental_execution_never_accepts_an_empty_scope(monkeypatch):
    calls = _capture_writes(monkeypatch)
    with pytest.raises(ValueError, match="at least one affected"):
        shared._apply_load_strategy(
            object(), table_name="students", target="unified", schema="dbo",
            processing={"load_strategy": "append"},
            scope={"read_strategy": "incremental", "partition_values": []},
        )
    assert calls == []
