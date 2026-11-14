"""Readable final pipeline summaries assembled from the finalized run snapshot."""

import json
from copy import deepcopy

import pytest
from datetime import UTC, datetime, timedelta
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
                "rows_read": 125,
                "metrics": {"rows_read": 125, "measurement_source": "returned_dataframe"},
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
                "rows_written": 170,
                "metrics": {"input_rows": 100, "versions_inserted": 100,
                            "versions_expired": 70, "rows_unchanged": 0,
                            "rows_committed": 170},
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
        ("Read", "wh_Bronze", "dbo", "orders", "full", "125", "—",
         "Batch returned", "Succeeded", "00:00:12", "Read: passed", "—", "—", "—"),
        ("Write", "Lakehouse_Silver", "dbo", "orders", "scd2", "—", "170",
         "100 processed, 100 versions inserted, 70 versions expired, 0 unchanged",
         "Succeeded", "00:00:45", "Write: passed; Profile: passed", "—", "—", "—"),
    ]


def test_missing_read_count_and_dry_run_write_are_not_reported_as_zero():
    """Unknown lazy read counts and non-published Dry Run targets stay explicit."""
    result = _result()
    result["execution_mode"] = "dry_run"
    result["operations"][0].pop("rows_read")
    result["operations"][0].pop("metrics")
    result["operations"][1].pop("rows_written")
    result["operations"][1].pop("metrics")
    pipeline = _pipeline(spark=None)
    pipeline.plan.evidence["operations"]["source:logical-orders"]["rows_read"] = None
    pipeline.plan.evidence["operations"]["target:logical-orders"].pop("rows_written")

    rows = finalize_module._operation_summary_rows(result, pipeline=pipeline)

    assert rows[0][5] == "Not captured"
    assert rows[1][6] == "Not published"


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
        "Operation", "Store", "Schema", "Table / File", "Mode",
        "Rows read", "Rows written", "Metrics", "Status", "Duration", "Stages",
        "Format", "Layout", "Publication",
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


@pytest.mark.parametrize("single_file,expected_layout", [(True, "Single file"), (False, "Dataset folder")])
@pytest.mark.parametrize("publication", ["published", "ignored", "not_published"])
def test_file_summary_uses_source_identity_and_retained_output_metrics(single_file, expected_layout, publication):
    """File destinations and output counts are visible without fabricating committed rows."""
    result = _result()
    source, target = result["operations"]
    for operation in (source, target):
        operation.update(source_type="file", source_id="file:" + operation["table_id"], table_id=None,
                         destination={"source_type": "file", "relative_path": "demo/orders.csv", "file_format": "csv"})
    target.update(file_write_parameters_json=json.dumps({"single_file": single_file}),
                  publication_status=publication, rows_written=None,
                  metrics={"input_rows": 120, "file_count": 1, "output_bytes": 8192, "rows_committed": None})
    pipeline = _pipeline(None)
    pipeline.plan.participants_json = json.dumps({
        source["source_id"]: {"store": "Bronze", "source_type": "file"},
        target["source_id"]: {"store": "Silver", "source_type": "file"},
    })
    pipeline.plan.evidence = {"operations": {}}
    before = deepcopy(result)

    rows = finalize_module._operation_summary_rows(result, pipeline=pipeline)

    assert rows[0][1:4] == ("Bronze", "—", "Files/demo/orders.csv")
    assert rows[0][-3:] == ("csv", "—", "—")
    assert rows[1][1:4] == ("Silver", "—", "Files/demo/orders.csv")
    assert rows[1][6] == "Not captured"
    assert rows[1][7] == "120 processed, 1 files in output, 8,192 bytes in output"
    assert rows[1][-3:] == ("csv", expected_layout, publication.replace("_", " ").title())
    assert result == before


@pytest.mark.parametrize("parameters", [None, "invalid JSON", "null"])
def test_file_summary_missing_history_stays_not_captured(parameters):
    """Historical files retain their destination without invented publication details."""
    result = _result()
    target = result["operations"][1]
    target.update(source_type="file", source_id="file:target", table_id=None,
                  destination={"source_type": "file", "relative_path": "exports/orders", "file_format": "parquet"},
                  file_write_parameters_json=parameters, rows_written=None, metrics={})

    row = finalize_module._operation_summary_rows(result)[1]

    assert row[2:4] == ("—", "Files/exports/orders")
    assert row[6:8] == ("Not captured", "Not captured")
    assert row[-3:] == ("parquet", "Not captured", "Not Captured")


def test_file_dry_run_summary_uses_runtime_fallback_without_publication_counts():
    """A prepared file Write shows its layout and honest Dry Run publication state."""
    result = _result()
    result["execution_mode"] = "dry_run"
    target = result["operations"][1]
    target.update(source_type="file", source_id="file:target", table_id=None,
                  destination={"source_type": "file", "relative_path": "exports/orders.csv", "file_format": "csv"},
                  rows_written=None, metrics={})
    pipeline = _pipeline(None)
    pipeline.plan.evidence["operations"][target["operation_key"]] = {
        "store": "Silver", "publication_status": "not_published",
        "file_write_parameters_json": json.dumps({"single_file": True}),
        "metrics": {"input_rows": 0},
    }

    row = finalize_module._operation_summary_rows(result, pipeline=pipeline)[1]

    assert row[1] == "Silver"
    assert row[6:8] == ("Not published", "0 processed")
    assert row[-3:] == ("csv", "Single file", "Not Published")
