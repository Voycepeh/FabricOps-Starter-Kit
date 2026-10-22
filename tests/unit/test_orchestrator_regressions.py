"""Regression coverage for governed Read and Write boundary failures."""

from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit.pipeline import shared
from tests.helpers import execution_plan_stub, execution_context_stub
from tests.helpers import run_pipeline_operation
PLAN = execution_plan_stub()

read = import_module("fabricops_kit.pipeline.orchestrate_read")
write = import_module("fabricops_kit.pipeline.orchestrate_write")


@pytest.fixture
def read_runtime(monkeypatch):
    """Keep stage planning real while isolating physical source access."""
    context = execution_context_stub({"source": None}, {"source": [{"guardrail_type": "grain"}]})
    monkeypatch.setattr(read, "resolve_table_id", Mock(return_value="source"))
    monkeypatch.setattr(read, "prepare_pipeline_execution", Mock(return_value=context))
    frame = SimpleNamespace(columns=["id"])
    reader = Mock(side_effect=lambda **kwargs: {
        "table_id": "source", "dataframe": frame, "read_mode": kwargs["read_mode"],
        "is_query": kwargs["query"] is not None,
    })
    grain = Mock(return_value={"status": "passed", "can_continue": True})
    profile = Mock(return_value={"row_count": 3})
    monkeypatch.setattr(read, "pipeline_read", reader)
    monkeypatch.setattr(read, "check_grain", grain)
    monkeypatch.setattr(read, "profile_table", profile)
    return reader, grain, profile


@pytest.mark.parametrize("mode", ["full", "FULL", " Full ", "\tFuLl\n"])
def test_full_mode_normalized_for_reader_grain_profile_and_summary(read_runtime, mode):
    """Every accepted spelling executes the same full lifecycle and reports its count."""
    reader, grain, profile = read_runtime
    result = run_pipeline_operation(read.orchestrate_read, plan=PLAN, store="Bronze", schema="demo", table_name="orders", read_mode=mode, verbose=False)
    assert result["read_mode"] == "full"
    assert reader.call_args.kwargs["read_mode"] == "full"
    assert grain.call_args.kwargs["scope"] == "read_full"
    profile.assert_called_once()
    assert result["orchestration_stages"][-1]["stage"] == "Profile"
    assert result["read_metrics"]["rows_read"] == 3


@pytest.mark.parametrize("mode", ["incremental", "INCREMENTAL", " Incremental "])
def test_incremental_mode_normalized_for_reader_parameters_and_grain(read_runtime, mode):
    """Incremental spellings preserve parameters, use batch Grain, and skip Profile."""
    reader, grain, profile = read_runtime
    parameters = {"watermark_column": "modified_at"}
    result = run_pipeline_operation(read.orchestrate_read, plan=PLAN, store="Bronze", schema="demo", table_name="orders", read_mode=mode,
                                   read_parameters=parameters, target_table_id="target", verbose=False)
    assert reader.call_args.kwargs["read_mode"] == "incremental"
    assert reader.call_args.kwargs["read_parameters"] is parameters
    assert grain.call_args.kwargs["scope"] == "read_incremental_batch"
    assert result["profile_result"]["reason"] == "Incremental batch"
    profile.assert_not_called()


@pytest.mark.parametrize("mode", [None, "", " ", "delta", 7])
def test_invalid_read_mode_rejected_before_metadata_or_physical_read(read_runtime, mode):
    """Invalid modes cannot resolve contracts, read data, or run stages."""
    with pytest.raises(ValueError, match="read_mode"):
        run_pipeline_operation(read.orchestrate_read, plan=PLAN, store="Bronze", schema="demo", table_name="orders", read_mode=mode)
    read.resolve_table_id.assert_not_called()
    read.prepare_pipeline_execution.assert_not_called()
    read_runtime[0].assert_not_called()


def test_internal_reader_normalizes_before_incremental_parameter_checks(monkeypatch):
    """Parameter validation sees the same canonical mode as the public orchestrator."""
    module = import_module("fabricops_kit.pipeline.pipeline_read")
    resolve = Mock(side_effect=RuntimeError("reached identity resolution"))
    monkeypatch.setattr(module, "resolve_physical_table_identity", resolve)
    with pytest.raises(RuntimeError, match="reached identity resolution"):
        module.pipeline_read(store="Bronze", table_name="orders", read_mode=" INCREMENTAL ",
                             read_parameters={"watermark_column": "modified_at"}, target_table_id="target",
                             context={"config": object(), "env": "dev"})
    resolve.assert_called_once()


@pytest.mark.parametrize("query", ["SELECT id FROM demo.orders", "SELECT COUNT(*) AS n FROM demo.orders"])
def test_query_profile_does_not_receive_physical_table_identity(read_runtime, query):
    """Derived schema and statistics cannot be saved as the physical source snapshot."""
    reader, _grain, profile = read_runtime
    result = run_pipeline_operation(read.orchestrate_read, plan=PLAN, store="Gold", schema="demo", table_name="orders", query=query, verbose=False)
    assert result["is_query"] is True
    assert result["table_id"] == "source"
    assert profile.call_args.kwargs["dataframe"] is result["dataframe"]
    assert not {"table_id", "store", "schema", "table_name"} & profile.call_args.kwargs.keys()
    assert reader.call_args.kwargs["query"] == query


def test_query_uses_real_dataframe_profile_without_metadata_writes(read_runtime, monkeypatch, spark_session):
    """The actual Profile path leaves all physical table metadata untouched."""
    profile_module = import_module("fabricops_kit.pipeline.profile_table")
    monkeypatch.setattr(read, "profile_table", profile_module.profile_table)
    frame = spark_session.range(4).selectExpr("count(*) AS order_count")
    reader, _grain, _profile = read_runtime
    reader.side_effect = None
    reader.return_value = {"table_id": "source", "dataframe": frame, "is_query": True, "read_mode": "full"}
    metadata = []
    for name in ("resolve_fabric_context", "_upsert_catalogue_identities", "_replace_snapshot_rows", "_replace_frequency_rows"):
        mock = Mock(side_effect=AssertionError("query profiling must not access table metadata"))
        monkeypatch.setattr(profile_module, name, mock)
        metadata.append(mock)
    result = run_pipeline_operation(read.orchestrate_read, plan=PLAN, store="Gold", schema="demo", table_name="orders",
                                   query="SELECT COUNT(*) AS order_count FROM demo.orders",
                                   spark_session=spark_session, frequency_enabled=False, verbose=False)
    assert len(result["profile_result"]["profile"].collect()) == 1
    for mock in metadata:
        mock.assert_not_called()












def test_profile_failure_exposes_completed_publication_and_original_cause(monkeypatch, capsys):
    """Post-commit failure preserves diagnostics without suggesting the write rolled back."""
    context = execution_context_stub({"target": None})
    monkeypatch.setattr(write, "resolve_table_id", lambda **_kwargs: "target")
    monkeypatch.setattr(write, "prepare_pipeline_execution", lambda *_args, **_kwargs: context)
    publish = Mock(return_value={"table_id": "target", "strategy": "append", "write_metrics": {"rows_committed": 4}})
    monkeypatch.setattr(write, "pipeline_write", publish)
    cause = ValueError("profile service unavailable")
    monkeypatch.setattr(write, "profile_table", Mock(side_effect=cause))
    with pytest.raises(RuntimeError, match="publication and checkpoint finalization already succeeded") as raised:
        run_pipeline_operation(write.orchestrate_write, SimpleNamespace(columns=["id"]), plan=PLAN, sources=[], store="Silver", schema="demo",
                                table_name="orders", write_mode="append")
    assert raised.value.published is True
    assert raised.value.table_id == "target"
    assert raised.value.write_metrics["rows_committed"] == 4
    assert raised.value.failed_stage == "Profile"
    assert raised.value.__cause__ is cause
    publish.assert_called_once()
    assert "already succeeded" in capsys.readouterr().out


@pytest.fixture(autouse=True)
def isolated_operation_journal(monkeypatch):
    """Stage unit tests isolate run storage; lifecycle tests exercise the real journal."""
    from contextlib import nullcontext
    from importlib import import_module
    from unittest.mock import Mock

    for name in ("orchestrate_read", "orchestrate_write"):
        monkeypatch.setattr(import_module(f"fabricops_kit.pipeline.{name}"), "PipelineOperation",
                            lambda _plan, _role, arguments: nullcontext(Mock(arguments=arguments)))
