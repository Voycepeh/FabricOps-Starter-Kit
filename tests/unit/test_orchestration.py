"""Focused tests for standard pipeline orchestration."""
from unittest.mock import Mock, patch
import pytest
import importlib
from types import SimpleNamespace
from tests.helpers import run_pipeline_operation

LIVE_PLAN = SimpleNamespace(execution_mode="live", plan_id="plan", permits_persistence=True, runtime_context={}, workspace_id="dev", results=[], simulations=[])


def test_dq_stage_prints_observed_percentages_independently_of_decision(capsys):
    """A passed tolerance decision must still display the observed violation rate."""
    from fabricops_kit.pipeline.shared import _run_orchestration_stage

    _run_orchestration_stage(operation="READ", name="orders", index=1, total=1, stage="Data Quality",
                             function=lambda: {"status": "passed", "summary": {
                                 "DQ_PASSED_ROW_PERCENT": 99.0, "DQ_FAILED_ROW_PERCENT": 1.0,
                                 "DQ_NOT_APPLICABLE_ROW_COUNT": 2,
                             }}, verbose=True)
    output = capsys.readouterr().out
    assert "99.00% pass" in output and "1.00% with violations" in output
    assert "2 not applicable" in output and "Passed" in output


@pytest.mark.parametrize("operation", ["read", "write"])
def test_invalid_dq_diagnostics_fails_before_io(operation):
    """Do not run a source read or target write with an invalid diagnostics choice."""
    module = importlib.import_module(f"fabricops_kit.pipeline.orchestrate_{operation}")
    with patch.object(module, "resolve_table_id", side_effect=AssertionError("unexpected IO")):
        with pytest.raises(ValueError, match="dq_diagnostics"):
            options = {"store": "Bronze", "schema": "demo", "table_name": "orders", "dq_diagnostics": "invalid"}
            if operation == "read":
                run_pipeline_operation(module.orchestrate_read, plan=LIVE_PLAN, **options)
            else:
                run_pipeline_operation(module.orchestrate_write, object(), plan=LIVE_PLAN, sources=[], write_mode="overwrite", **options)



@pytest.fixture(autouse=True)
def planned_stages(monkeypatch):
    """Isolate stage ordering from metadata planning; integration tests exercise planning."""
    monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline.orchestrate_write"), "source_guardrail_results", lambda *_args: [])
    def prepare(table_ids, **_kwargs):
        return {"config": object(), "scope_workspace_id": "dev", "execution_plan": LIVE_PLAN,
                "_pipeline_identities": {tid: {"roles": ["source", "target"]} for tid in table_ids},
                "_pipeline_contracts": {tid: {"contract_id": "contract", "contract_version": 1} for tid in table_ids},
                "_pipeline_rules": {tid: [{"guardrail_type": kind} for kind in
                    ("schema", "freshness", "sensitive_data", "data_quality", "source_drift")] for tid in table_ids}}
    monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline.orchestrate_read"), "prepare_pipeline_execution", prepare)
    monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline.orchestrate_write"), "prepare_pipeline_execution", prepare)
    monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline.orchestrate_read"), "resolve_table_id", lambda **_kwargs: "source-id")

def test_orchestrate_read_orders_stages_and_preserves_source(capsys):
    """Read stages run in order and retain source identity."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read
    dataframe = object()
    calls = []
    def result(name, value):
        def call(*args, **kwargs): calls.append(name); return value
        return call
    with patch("fabricops_kit.pipeline.orchestrate_read.pipeline_read", result("read", {"dataframe": dataframe, "table_id": "source-id"})), patch("fabricops_kit.pipeline.orchestrate_read.check_freshness", result("freshness", {"status": "passed"})), patch("fabricops_kit.pipeline.orchestrate_read.check_schema", result("schema", {"status": "passed"})), patch("fabricops_kit.pipeline.orchestrate_read.check_dq", result("dq", {"status": "passed"})), patch("fabricops_kit.pipeline.orchestrate_read.schedule_table_profiling", result("profile", {"profile": object()})):
        actual = run_pipeline_operation(orchestrate_read, plan=LIVE_PLAN, store="Bronze", schema="demo", table_name="orders", verbose=False)
    assert calls == ["read", "freshness", "schema", "dq", "profile"]
    assert actual["dataframe"] is dataframe
    assert actual["table_id"] == "source-id"
    assert actual["orchestration_stages"][1]["status"] == "passed"
    assert {stage["name"] for stage in actual["orchestration_stages"]} == {"orders"}
    assert capsys.readouterr().out == ""


def test_orchestrate_read_uses_table_name_for_heading_and_stage_metadata(capsys):
    """Read presentation and returned stage records use the physical table name."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read

    with patch(
        "fabricops_kit.pipeline.orchestrate_read.pipeline_read",
        return_value={"dataframe": object(), "table_id": "canonical-id"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_freshness",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_schema",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_dq",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.schedule_table_profiling",
        return_value={"status": "passed"},
    ):
        result = run_pipeline_operation(orchestrate_read, plan=LIVE_PLAN,
            store="Bronze", schema="demo", table_name="physical_orders"
        )

    assert "FabricOps READ · physical_orders" in capsys.readouterr().out
    assert {stage["name"] for stage in result["orchestration_stages"]} == {
        "physical_orders"
    }
    assert result["table_id"] == "canonical-id"


@pytest.mark.parametrize(
    ("function_path", "arguments"),
    [
        (
            "fabricops_kit.pipeline.orchestrate_read.orchestrate_read",
            {"store": "Bronze", "schema": "demo", "table_name": "orders"},
        ),
        (
            "fabricops_kit.pipeline.orchestrate_write.orchestrate_write",
            {
                "dataframe": object(),
                "store": "Silver",
                "schema": "demo",
                "table_name": "orders",
                "write_mode": "overwrite",
            },
        ),
    ],
)
def test_orchestrators_reject_obsolete_name_keyword(function_path, arguments):
    """The removed naming keyword fails through normal Python argument binding."""
    import importlib

    module_name, function_name = function_path.rsplit(".", 1)
    function = getattr(importlib.import_module(module_name), function_name)
    with pytest.raises(TypeError, match="unexpected keyword argument 'name'"):
        function(**arguments, name="legacy_label")


def test_orchestrate_read_reports_selected_physical_reader(capsys):
    """Read output surfaces the foundational reader selected by pipeline_read."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read

    source = {
        "dataframe": object(),
        "table_id": "source-id",
        "_reader_name": "read_warehouse_table",
    }
    with patch(
        "fabricops_kit.pipeline.orchestrate_read.pipeline_read", return_value=source
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_freshness",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_schema",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_dq",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.schedule_table_profiling",
        return_value={"status": "passed"},
    ):
        actual = run_pipeline_operation(orchestrate_read, plan=LIVE_PLAN,
            store="Product",
            schema="demo",
            table_name="order_history",
        )

    assert "_reader_name" not in actual
    assert "Physical reader → read_warehouse_table" in capsys.readouterr().out


def test_orchestrate_read_attributes_failure_and_stops_later_stages():
    """Read failures retain cause and stop later stages."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read
    cause = ValueError("meaningful schema mismatch")
    with patch("fabricops_kit.pipeline.orchestrate_read.pipeline_read", return_value={"dataframe": object(), "table_id": "source-id"}), patch("fabricops_kit.pipeline.orchestrate_read.check_freshness", return_value={"status": "passed"}), patch("fabricops_kit.pipeline.orchestrate_read.check_schema", side_effect=cause), patch("fabricops_kit.pipeline.orchestrate_read.check_dq") as dq:
        with pytest.raises(RuntimeError, match="READ 'orders' failed during Schema") as raised:
            run_pipeline_operation(orchestrate_read, plan=LIVE_PLAN, store="Bronze", schema="demo", table_name="orders", verbose=False)
    assert raised.value.__cause__ is cause
    dq.assert_not_called()


def test_orchestrate_write_orders_stages_and_profiles_after_write(capsys):
    """Write stages use prepared rows and profile after publication."""
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write
    dataframe, prepared = object(), object()
    calls = []
    def effect(name, value):
        def call(*args, **kwargs): calls.append(name); return value
        return call
    patches = [
        patch("fabricops_kit.pipeline.orchestrate_write.resolve_table_id", return_value="target-id"),
        patch("fabricops_kit.pipeline.orchestrate_write.check_schema", effect("schema", {"status":"passed"})),
        patch("fabricops_kit.pipeline.orchestrate_write.check_sensitive_data", effect("sensitive", {"status":"passed", "dataframe":prepared})),
        patch("fabricops_kit.pipeline.orchestrate_write.check_source_drift", effect("drift", {"status":"passed"})),
        patch("fabricops_kit.pipeline.orchestrate_write.check_dq", effect("dq", {"status":"passed"})),
        patch("fabricops_kit.pipeline.orchestrate_write.pipeline_write", side_effect=effect("write", {"table_id":"target-id"})),
        patch("fabricops_kit.pipeline.orchestrate_write.schedule_table_profiling", effect("profile", {"profile":object()})),
    ]
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as write, patches[6]:
        actual = run_pipeline_operation(orchestrate_write, dataframe, plan=LIVE_PLAN, sources=[{"table_id":"source-id", "execution_plan_id":"plan"}], store="Silver", schema="demo", table_name="physical_target", write_mode="overwrite")
    assert calls == ["schema", "sensitive", "drift", "dq", "write", "profile"]
    assert actual["published"] is True
    assert actual["table_id"] == "target-id"
    assert write.call_args.args[0] is prepared
    assert {stage["name"] for stage in actual["orchestration_stages"]} == {"physical_target"}
    output = capsys.readouterr().out
    assert "FabricOps WRITE · physical_target" in output
    assert "Strategy        → Overwrite" in output
    assert "Target          → Silver.demo.physical_target" in output
    assert "Rows committed  → Not available" in output


def test_orchestrate_write_forwards_scd_write_parameters(capsys):
    """SCD parameters are forwarded to pipeline_write without reinterpretation."""
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write

    prepared = object()
    scd2 = {
        "key_columns": ["product_id"],
        "effective_column": "modified_datetime",
        "tracked_columns": ["category"],
    }
    with patch(
        "fabricops_kit.pipeline.orchestrate_write.resolve_table_id",
        return_value="target-id",
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_schema",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_sensitive_data",
        return_value={"status": "passed", "dataframe": prepared},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_source_drift",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_dq",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.pipeline_write",
        return_value={"table_id": "target-id"},
    ) as write, patch(
        "fabricops_kit.pipeline.orchestrate_write.schedule_table_profiling",
        return_value={"profile": object()},
    ):
        run_pipeline_operation(orchestrate_write,
            object(),
            plan=LIVE_PLAN, sources=[],
            store="Silver",
            schema="demo",
            table_name="product_mapping_scd2",
            write_mode="scd2",
            write_parameters=scd2,
            verbose=False,
        )

    assert write.call_args.kwargs["load_strategy"] == "scd2"
    assert write.call_args.kwargs["load_strategy_parameters"] == scd2
    assert capsys.readouterr().out == ""


def test_orchestrate_write_preserves_guardrail_failure_and_does_not_write():
    """Write failures retain the Guardrail cause and prevent publication."""
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write
    cause = RuntimeError("blocking DQ rule: completeness 96.7%")
    with patch("fabricops_kit.pipeline.orchestrate_write.resolve_table_id", return_value="target-id"), patch("fabricops_kit.pipeline.orchestrate_write.check_schema", return_value={"status":"passed"}), patch("fabricops_kit.pipeline.orchestrate_write.check_sensitive_data", return_value={"status":"passed", "dataframe":object()}), patch("fabricops_kit.pipeline.orchestrate_write.check_source_drift", return_value={"status":"passed"}), patch("fabricops_kit.pipeline.orchestrate_write.check_dq", side_effect=cause), patch("fabricops_kit.pipeline.orchestrate_write.pipeline_write") as write:
        with pytest.raises(RuntimeError, match="WRITE 'physical_target' failed during Data Quality") as raised:
            run_pipeline_operation(orchestrate_write, object(), plan=LIVE_PLAN, sources=[{"table_id":"source-id", "execution_plan_id":"plan"}], store="Silver", schema="demo", table_name="physical_target", write_mode="overwrite", verbose=False)
    assert raised.value.__cause__ is cause
    write.assert_not_called()


def test_failed_stage_output_never_reports_passed_and_marks_later_stages_not_run(capsys):
    """User-facing output attributes failure without a contradictory pass."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read

    with patch(
        "fabricops_kit.pipeline.orchestrate_read.pipeline_read",
        return_value={"dataframe": object(), "table_id": "source-id"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_freshness",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_schema",
        side_effect=ValueError("schema mismatch"),
    ):
        with pytest.raises(RuntimeError):
            run_pipeline_operation(orchestrate_read, plan=LIVE_PLAN,
                store="Bronze",
                schema="demo",
                table_name="orders",
            )

    output = capsys.readouterr().out
    assert "[3/5] Schema ... ✗ Failed" in output
    assert "[3/5] Schema ... ✓ Passed" not in output
    assert "Later stages did not run." in output
    assert "FabricOps READ Summary" not in output


@pytest.mark.parametrize(
    ("capability_status", "orchestration_status"),
    [
        ("passed", "passed"),
        ("warning", "warning"),
        ("blocked", "blocked"),
        ("failed", "blocked"),
        ("skipped", "skipped"),
        ("unexpected-new-status", "warning"),
    ],
)
def test_orchestration_status_maps_capability_semantics(
    capability_status, orchestration_status
):
    """Capability PASS, WARN, BLOCK, and SKIP states are mapped deliberately."""
    from fabricops_kit.pipeline.shared import _orchestration_status

    assert _orchestration_status({"status": capability_status}) == orchestration_status


def test_orchestration_status_aggregates_multi_source_results():
    """A warning or block in one source cannot become a passed aggregate stage."""
    from fabricops_kit.pipeline.shared import _orchestration_status

    assert _orchestration_status([{"status": "passed"}, {"status": "warning"}]) == "warning"
    assert _orchestration_status([{"status": "passed"}, {"status": "blocked"}]) == "blocked"


def test_orchestration_stage_duration_is_two_decimal_seconds_with_minimum():
    """Stage inspection reports stable seconds instead of tiny scientific-notation values."""
    from fabricops_kit.pipeline.shared import _run_orchestration_stage

    with patch(
        "fabricops_kit.pipeline.shared.time.perf_counter",
        side_effect=[100.0, 100.000001],
    ):
        _result, record = _run_orchestration_stage(
            operation="READ",
            name="orders",
            index=1,
            total=1,
            stage="Read",
            function=lambda: {"status": "passed"},
            verbose=False,
        )

    assert record["duration_seconds"] == 0.01

    with patch(
        "fabricops_kit.pipeline.shared.time.perf_counter",
        side_effect=[100.0, 101.234],
    ):
        _result, record = _run_orchestration_stage(
            operation="WRITE",
            name="orders",
            index=1,
            total=1,
            stage="Write",
            function=lambda: {"status": "passed"},
            verbose=False,
        )

    assert record["duration_seconds"] == 1.23


@pytest.mark.parametrize("operation", ["read", "write"])
@pytest.mark.parametrize("parameter", ["grain_discovery_enabled", "frequency_enabled", "frequency_top_n"])
def test_orchestrators_reject_notebook_profiling_controls(operation, parameter):
    """Profiling configuration is table-scoped and cannot be overridden per operation."""
    module = importlib.import_module(f"fabricops_kit.pipeline.orchestrate_{operation}")
    function = getattr(module, f"orchestrate_{operation}")
    arguments = {"store": "Bronze", "schema": "demo", "table_name": "orders", parameter: False}
    if operation == "write":
        arguments.update(dataframe=object(), write_mode="overwrite")
    with pytest.raises(TypeError, match=parameter):
        function(**arguments)


def test_testing_blocked_stage_prints_diagnostics_and_retains_result(capsys):
    """A normal Testing violation must remain inspectable with verbose output enabled."""
    from fabricops_kit.pipeline.shared import _run_orchestration_stage
    result, stage = _run_orchestration_stage(operation="WRITE", name="orders", index=1, total=1,
        stage="Grain", function=lambda: {"status": "failed", "can_continue": False}, verbose=True, allow_blocked=True)
    assert not result["can_continue"] and stage["status"] == "blocked"
    assert "Blocked (diagnostic)" in capsys.readouterr().out


def test_stage_failure_retains_actual_publication_and_persistence_status():
    """Stage attribution must preserve the partial outcome returned by a native writer."""
    from fabricops_kit.pipeline.shared import _run_orchestration_stage
    failure = ValueError("metadata finalization failed")
    failure.published = True
    failure.persistence_status = "incomplete"
    failure.table_id = "target"
    def fail():
        raise failure
    with pytest.raises(RuntimeError) as raised:
        _run_orchestration_stage(operation="WRITE", name="orders", index=1, total=1, stage="Write", function=fail, verbose=False)
    assert raised.value.published is True and raised.value.persistence_status == "incomplete"
    assert raised.value.table_id == "target" and raised.value.__cause__ is failure


@pytest.mark.parametrize("stage", ["Schema", "Grain", "Data Quality", "Sensitive Data", "Source Drift"])
def test_required_unexecuted_guardrail_fails_live_and_keeps_testing_input(stage):
    """An unexecuted check cannot authorize Live or discard Testing's prepared input."""
    from fabricops_kit.pipeline.shared import _run_orchestration_stage
    frame = object()
    outcome = {"status": "skipped", "can_continue": True, "dataframe": frame}
    value = [outcome] if stage == "Source Drift" else outcome
    options = dict(operation="WRITE", name="orders", index=1, total=1, stage=stage,
                   function=lambda: value, verbose=False)
    with pytest.raises(RuntimeError, match="configured Guardrail did not execute"):
        _run_orchestration_stage(**options)
    result, record = _run_orchestration_stage(**options, allow_blocked=True)
    actual = result[0] if isinstance(result, list) else result
    assert actual["dataframe"] is frame and actual["can_continue"] is False
    assert record["status"] == "blocked" and record["evaluation_status"] == "not_fully_evaluated"


def test_static_freshness_is_an_intentional_contract_opt_out():
    """No refresh expected is a saved policy rather than an unavailable required check."""
    from fabricops_kit.pipeline.shared import _run_orchestration_stage
    result, record = _run_orchestration_stage(operation="READ", name="static", index=1, total=1,
        stage="Freshness", function=lambda: {"status": "skipped", "rule_type": "skip", "can_continue": True}, verbose=False)
    assert result["can_continue"] and record["status"] == "skipped"


@pytest.fixture(autouse=True)
def isolated_operation_journal(monkeypatch):
    """Stage unit tests isolate run storage; lifecycle tests exercise the real journal."""
    from contextlib import nullcontext
    from importlib import import_module

    for name in ("orchestrate_read", "orchestrate_write"):
        monkeypatch.setattr(import_module(f"fabricops_kit.pipeline.{name}"), "PipelineOperation",
                            lambda _plan, _role, arguments: nullcontext(Mock(arguments=arguments)))
