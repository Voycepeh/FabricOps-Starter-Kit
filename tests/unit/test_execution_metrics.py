"""Execution metrics use commit evidence and existing aggregates, never counts."""
# ruff: noqa: D102, D103, D107
from contextlib import ExitStack
from importlib import import_module
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from fabricops_kit.io.shared import DeltaCommitMetrics
from fabricops_kit.pipeline.shared import ExecutionSummary


def _metadata_runtime(lines, *, entries=1, fail=False):
    """Emulate only Hadoop metadata APIs; Spark actions are absent."""
    reader = Mock()
    reader.readLine.side_effect = [*lines, None]
    fs = Mock()
    iterator = Mock()
    iterator.hasNext.side_effect = [True] * entries + [False]
    iterator.next.return_value.getPath.return_value.getName.return_value = "00000000000000000001.json"
    fs.listStatusIterator.return_value = iterator
    path = Mock()
    path.getFileSystem.return_value = fs
    jvm = Mock()
    jvm.org.apache.hadoop.fs.Path.return_value = path
    jvm.java.io.BufferedReader.return_value = reader
    if fail:
        fs.listStatusIterator.side_effect = OSError("metadata unavailable")
    return SimpleNamespace(_jvm=jvm, _jsc=Mock()), reader


@pytest.mark.parametrize("rows", [0, 8, 9000000000])
def test_delta_metrics_read_exact_tagged_commit(rows):
    attempt = DeltaCommitMetrics()
    spark, reader = _metadata_runtime([json.dumps({"commitInfo": {
        "userMetadata": attempt.token, "operation": "WRITE",
        "operationMetrics": {"numOutputRows": str(rows)},
    }})])
    assert attempt.read(spark, "/table") == rows
    reader.close.assert_called_once()


@pytest.mark.parametrize("change", [
    {"userMetadata": "another-writer"}, {"operation": "MERGE"},
    {"operationMetrics": {}}, {"operationMetrics": {"numOutputRows": "-1"}},
    {"operationMetrics": {"numOutputRows": True}},
])
def test_unattributable_or_unsupported_delta_metrics_are_unavailable(change):
    attempt = DeltaCommitMetrics()
    info = {"userMetadata": attempt.token, "operation": "WRITE", "operationMetrics": {"numOutputRows": "8"}}
    spark, reader = _metadata_runtime([json.dumps({"commitInfo": {**info, **change}})])
    assert attempt.read(spark, "/table") is None
    reader.close.assert_called_once()


def test_delta_metrics_bound_metadata_io_and_ignore_lookup_errors():
    spark, reader = _metadata_runtime([], entries=257)
    assert DeltaCommitMetrics().read(spark, "/table") is None
    reader.readLine.assert_not_called()
    spark, _ = _metadata_runtime([], fail=True)
    assert DeltaCommitMetrics().read(spark, "/table") is None


@pytest.mark.parametrize("mode,rows", [("overwrite", 8), ("append", 3), ("append", 0)])
def test_physical_writer_reports_committed_rows_without_counting(mode, rows):
    module = import_module("fabricops_kit.io.write_lakehouse_table")
    frame = SimpleNamespace(write=object(), sparkSession=object())
    metrics = {}
    with patch.object(module, "resolve_configured_lakehouse_table", return_value=(None, "orders", "demo", "/table")), patch.object(module, "repartition_dataframe_for_write", return_value=frame), patch.object(module, "write_delta_path") as write, patch.object(DeltaCommitMetrics, "read", return_value=rows):
        result = module.write_lakehouse_table(frame, "orders", mode=mode, verbose=False, context={"_fabricops_write_metrics": metrics})
    assert result is None  # Live physical writer contract is unchanged.
    assert metrics["rows_committed"] == rows
    assert metrics["measurement_source"] == "delta_commit"
    assert write.call_args.kwargs["options"]["userMetadata"].startswith("fabricops-metrics:")
    if mode == "append":
        assert metrics["rows_inserted"] == rows


def test_failed_write_never_reads_or_reports_success_metrics():
    module = import_module("fabricops_kit.io.write_lakehouse_table")
    frame = SimpleNamespace(write=object())
    metrics = {}
    with patch.object(module, "resolve_configured_lakehouse_table", return_value=(None, "orders", None, "/table")), patch.object(module, "repartition_dataframe_for_write", return_value=frame), patch.object(module, "write_delta_path", side_effect=RuntimeError("failed commit")), patch.object(DeltaCommitMetrics, "read") as read:
        with pytest.raises(RuntimeError, match="failed commit"):
            module.write_lakehouse_table(frame, "orders", context={"_fabricops_write_metrics": metrics})
    assert metrics == {}
    read.assert_not_called()


def test_summary_duration_is_wall_clock_and_unknown_values_are_explicit(capsys):
    with patch("fabricops_kit.pipeline.shared.time.perf_counter", side_effect=[10, 98.554]):
        summary = ExecutionSummary("WRITE", verbose=True)
        assert summary.finish([("Rows committed", None), ("Rows inserted", 0)]) == 88.55
    output = capsys.readouterr().out
    assert "FabricOps WRITE Summary" in output
    assert "Rows committed  → Not available" in output
    assert "Rows inserted   → 0" in output
    assert "Total duration  → 88.55s" in output


@pytest.mark.parametrize("mode", ["overwrite", "append", "scd1", "scd2"])
def test_write_summary_keeps_profile_total_separate_from_committed(mode, capsys):
    module = import_module("fabricops_kit.pipeline.orchestrate_write")
    frame = SimpleNamespace(columns=["id", "value"])
    with ExitStack() as stack:
        for name in ("resolve_table_id", "check_schema", "check_source_drift", "check_dq", "check_guardrail_coverage"):
            stack.enter_context(patch.object(module, name, return_value="target" if name == "resolve_table_id" else {"status": "passed"}))
        stack.enter_context(patch.object(module, "check_sensitive_data", return_value={"dataframe": frame}))
        stack.enter_context(patch.object(module, "pipeline_write", return_value={"table_id": "target", "strategy": mode, "write_metrics": {"rows_committed": 8 if mode in {"append", "overwrite"} else None}}))
        stack.enter_context(patch.object(module, "profile_table", return_value={"row_count": 100}))
        result = module.orchestrate_write(frame, sources=[], store="Silver", schema="demo", table_name="orders", write_mode=mode)
    assert result["write_metrics"]["total_target_rows"] == 100
    assert result["write_metrics"]["input_rows"] is None
    assert result["write_metrics"]["input_columns"] == 2
    assert result["write_metrics"]["rows_committed"] == (8 if mode in {"append", "overwrite"} else None)
    output = capsys.readouterr().out
    assert "FabricOps WRITE Summary" in output
    assert "Published       → Yes" in output
    if mode == "scd1":
        assert "Rows updated    → Not available" in output
    if mode == "scd2":
        assert "Versions expired → Not available" in output


@pytest.mark.parametrize("incremental,rows", [(False, 8), (True, 0), (True, None)])
def test_read_summary_reuses_profile_only_for_full_scope(incremental, rows, capsys):
    module = import_module("fabricops_kit.pipeline.orchestrate_read")
    source = {"dataframe": SimpleNamespace(columns=["id"]), "table_id": "source", "read_metrics": {"rows_read": rows if incremental else None}, "_reader_name": "read_warehouse_query"}
    with ExitStack() as stack:
        stack.enter_context(patch.object(module, "pipeline_read", return_value=source))
        for name in ("check_freshness", "check_schema", "check_dq"):
            stack.enter_context(patch.object(module, name, return_value={"status": "passed"}))
        profile = stack.enter_context(patch.object(module, "profile_table", return_value={"row_count": 8}))
        result = module.orchestrate_read(store="Gold", schema="demo", table_name="orders", read_mode="incremental" if incremental else "full")
    assert result["read_metrics"] == {"rows_read": rows, "columns": 1}
    assert "FabricOps READ Summary" in capsys.readouterr().out
    assert profile.call_count == (0 if incremental else 1)


@pytest.mark.parametrize("key", ["userMetadata", "USERMETADATA"])
def test_caller_commit_metadata_is_preserved_without_unattributable_lookup(key):
    module = import_module("fabricops_kit.io.write_lakehouse_table")
    frame = SimpleNamespace(write=object())
    options = {key: "caller-provided"}
    metrics = {"rows_committed": None}
    with patch.object(module, "resolve_configured_lakehouse_table", return_value=(None, "orders", None, "/table")), patch.object(module, "repartition_dataframe_for_write", return_value=frame), patch.object(module, "write_delta_path") as write, patch.object(DeltaCommitMetrics, "read") as read:
        module.write_lakehouse_table(frame, "orders", options=options, verbose=False, context={"_fabricops_write_metrics": metrics})
    assert write.call_args.kwargs["options"] == options
    assert options == {key: "caller-provided"}
    assert metrics["rows_committed"] is None
    read.assert_not_called()
