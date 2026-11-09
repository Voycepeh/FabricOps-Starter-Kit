"""Historical publication receipts remain verifiable without a strategy alias."""
# ruff: noqa: D103
from types import SimpleNamespace
import pytest
from fabricops_kit.pipeline import shared


def test_historical_append_receipts_remain_verifiable_without_strategy_alias(monkeypatch):
    monkeypatch.setattr(shared, "read_warehouse_query", lambda *a, **kw:
                        SimpleNamespace(first=lambda: {"fabricops_publication_rows": 1}))
    receipt = dict(strategy="append", activity_id="historical", committed_at="2026-01-01T00:00:00+00:00", input_rows=1)
    assert shared._physical_target_has_publication(dict(store_type="warehouse", store="Silver", schema="dbo", table_name="target"), receipt, context={})
    with pytest.raises(ValueError, match="invalid load_strategy"):
        shared.validated_processing({"load_strategy": "append"})
