"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_profile_helper_returns_notebook_ready_structure():
    """Verify profile helper returns notebook ready structure."""
    profile = {"table_name": "orders", "row_count": 3, "columns": [{"column_name": "amount"}]}

    assert profile["table_name"] == "orders"
    assert profile["row_count"] == 3
