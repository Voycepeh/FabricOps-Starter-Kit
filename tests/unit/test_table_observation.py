"""Tests for internal current-run Source Observation state."""
# ruff: noqa: D103
from __future__ import annotations

import fabricops_kit
import pytest

from fabricops_kit.pipeline import shared


def test_observe_table_is_not_public() -> None:
    assert not hasattr(fabricops_kit, "observe_table")
    assert "observe_table" not in fabricops_kit.__all__


def test_current_observations_are_tracked_independently_by_table_id() -> None:
    shared.set_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-a", observation=[{"source": "a"}]
    )
    shared.set_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-b", observation=[{"source": "b"}]
    )
    assert shared.get_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-a"
    ) == [{"source": "a"}]
    assert shared.get_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source-b"
    ) == [{"source": "b"}]


def test_missing_current_observation_requires_pipeline_read() -> None:
    with pytest.raises(ValueError, match=r"call pipeline_read\(\) first"):
        shared.get_current_source_observation(
            environment_name="dev", activity_id="missing", table_id="source-a"
        )


def test_capture_reuses_pipeline_read_dataframe_without_rescanning(monkeypatch) -> None:
    class Spark:
        def createDataFrame(self, rows):  # noqa: N802
            return list(rows)

    dataframe = type("Frame", (), {"columns": ["partition", "changed", "value"]})()
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(shared, "get_spark_session", Spark)
    monkeypatch.setattr(shared, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": "source-a", "store": "source", "schema": "dbo",
        "table_name": "orders", "store_type": "lakehouse",
    })
    monkeypatch.setattr(shared, "get_store", lambda *args, **kwargs: type("Store", (), {"schema_enabled": False})())
    monkeypatch.setattr(shared, "resolve_lakehouse_table_location", lambda *args: ("orders", "dbo", "path"))
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *args, **kwargs: [object()])
    monkeypatch.setattr(
        shared,
        "select_table_guardrail_rule",
        lambda *args, **kwargs: object()
        if kwargs.get("guardrail_type") == "source_drift"
        else None,
    )
    monkeypatch.setattr(shared, "resolve_source_drift_observation_columns", lambda rule: ("partition", "changed"))
    monkeypatch.setattr(shared, "_observe_dataframe", lambda frame, *args: [{
        "partition_value": "p", "row_count": 1, "min_change_value": "1",
        "max_change_value": "1", "content_fingerprint": "hash", "is_present": True,
    }])
    monkeypatch.setattr(shared, "_observe_lakehouse", lambda *args, **kwargs: pytest.fail("rescanned source"))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: {
        "_activity_id": "run", "_committed_at": "2026-09-13T00:00:00+00:00",
    })
    monkeypatch.setattr(shared, "coerce_metadata_row_types", lambda table, row: row)
    result = shared.capture_source_observation(table_id="source-a", dataframe=dataframe)
    assert result[0]["source_table_id"] == "source-a"
