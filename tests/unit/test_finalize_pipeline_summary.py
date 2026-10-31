"""Readable final pipeline summaries assembled from the finalized run snapshot."""

from datetime import UTC, datetime, timedelta
import json
from importlib import import_module
from types import SimpleNamespace

finalize_module = import_module("fabricops_kit.pipeline.finalize_pipeline")


def _result():
    started = datetime(2026, 10, 31, 7, 0, tzinfo=UTC)
    completed = started + timedelta(seconds=93)
    return {
        "run_id": "run-123",
        "pipeline_id": "pipeline-456",
        "execution_mode": "ungoverned",
        "status": "ungoverned_completed",
        "started_at": started,
        "completed_at": completed,
        "operations": [
            {
                "pipeline_role": "source",
                "operation_key": "source:logical-orders",
                "read_mode": "full",
                "table_id": "source-id",
                "destination": {"schema": "dbo", "table_name": "orders"},
                "status": "succeeded",
                "started_at": started,
                "completed_at": started + timedelta(seconds=12),
                "stages": [{"stage": "Read", "status": "passed"}],
            },
            {
                "pipeline_role": "target",
                "operation_key": "target:logical-orders",
                "write_mode": "scd2",
                "table_id": "target-id",
                "destination": {"schema": "dbo", "table_name": "orders"},
                "status": "succeeded",
                "started_at": started,
                "completed_at": started + timedelta(seconds=45),
                "stages": [{"stage": "Write", "status": "passed"},
                           {"stage": "Profile", "status": "passed"}],
            },
        ],
        "failures": [],
    }


def _pipeline(spark):
    identities = {
        "source-id": {
            "store": "wh_Bronze", "schema": "dbo", "table_name": "orders",
            "logical_id": "logical-orders",
        },
        "target-id": {
            "store": "Lakehouse_Silver", "schema": "dbo", "table_name": "orders",
            "logical_id": "logical-orders",
        },
    }
    evidence = {
        "operations": {
            "source:logical-orders": {"rows_read": 25000},
            "target:logical-orders": {"rows_written": 24850},
        }
    }
    return SimpleNamespace(
        spark=spark,
        pipeline_id="fallback-pipeline",
        plan=SimpleNamespace(
            plan_id="fallback-run",
            participants_json=json.dumps(identities),
            evidence=evidence,
        ),
    )


def test_operation_summary_rows_use_native_operation_metadata():
    """The display rows are projections of the finalized operation records."""
    rows = finalize_module._operation_summary_rows(
        _result(), pipeline=_pipeline(spark=None)
    )

    assert rows == [
        ("Read", "wh_Bronze", "dbo", "orders", "full", "—", "25,000", "—",
         "Succeeded", "00:00:12", "Read: passed"),
        ("Write", "Lakehouse_Silver", "dbo", "orders", "—", "scd2", "—", "24,850",
         "Succeeded", "00:00:45", "Write: passed; Profile: passed"),
    ]


def test_pipeline_summary_displays_dataframe_and_run_totals(monkeypatch, capsys):
    """Fabric notebook output contains a DataFrame and counts from stored operations."""
    captured = {}
    frame = object()

    class FakeSpark:
        def createDataFrame(self, rows, schema):
            captured["rows"] = rows
            captured["schema"] = schema
            return frame

    monkeypatch.setattr(
        finalize_module,
        "display",
        lambda value: captured.update(displayed=value),
        raising=False,
    )
    pipeline = _pipeline(FakeSpark())

    finalize_module._print_pipeline_summary(pipeline, _result())

    output = capsys.readouterr().out
    assert "UNGOVERNED COMPLETED" in output
    assert "Reads: 1 | Writes: 1 | Duration: 00:01:33" in output
    assert "Pipeline ID: pipeline-456" in output
    assert captured["displayed"] is frame
    assert captured["schema"] == [
        "Operation", "Store", "Schema", "Table", "Read mode", "Write mode",
        "Rows read", "Rows written", "Status", "Duration", "Stages",
    ]
    assert len(captured["rows"]) == 2


def test_pipeline_summary_shows_failure_codes_and_missing_duration(capsys):
    """Failure diagnostics stay sanitized and missing timing is labelled honestly."""
    result = _result()
    result["failures"] = [
        {"code": "project_execution_failed", "exception_type": "ValueError"}
    ]
    result["started_at"] = None
    pipeline = SimpleNamespace(
        spark=SimpleNamespace(
            createDataFrame=lambda rows, schema: SimpleNamespace(
                show=lambda **kwargs: None
            )
        ),
        pipeline_id="pipeline-456",
        plan=SimpleNamespace(
            plan_id="run-123",
            participants_json=json.dumps({}),
            evidence={"operations": {}},
        ),
    )

    finalize_module._print_pipeline_summary(pipeline, result)

    output = capsys.readouterr().out
    assert "Duration: Not captured" in output
    assert "project_execution_failed (ValueError)" in output
    assert "password" not in output
