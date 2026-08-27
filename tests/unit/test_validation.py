"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations
import pytest

from fabricops_kit.pipeline.shared import stop_if_failed, schema_check_core

pytestmark = pytest.mark.unit


def test_runtime_schema_check_supports_strict_allow_new_and_monitor_modes():
    """Verify validate schema supports strict allow new and monitor modes."""
    class FakeFrame:
        def __init__(self, dtypes):
            self.dtypes = dtypes
            self.columns = [name for name, _dtype in dtypes]

    df = FakeFrame([("id", "bigint"), ("amount", "double"), ("new_col", "string")])
    expected = {"id": "bigint", "amount": "double"}

    strict = schema_check_core(df, expected, preset="strict")
    allow_new = schema_check_core(df, expected, preset="allow_new_columns")
    monitor = schema_check_core(FakeFrame([("id", "bigint")]), expected, preset="monitor_only")

    assert strict["status"] == "failed"
    assert strict["can_continue"] is False
    assert allow_new["status"] == "warning"
    assert allow_new["can_continue"] is True
    assert monitor["status"] == "warning"
    assert monitor["can_continue"] is True
    with pytest.raises(ValueError, match="preset"):
        schema_check_core(df, expected, preset="unknown")
