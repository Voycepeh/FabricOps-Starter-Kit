"""Focused tests for standard pipeline orchestration."""
from unittest.mock import Mock, patch
import pytest


def test_orchestrate_read_orders_stages_and_preserves_source():
    """Read stages run in order and retain source identity."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read
    dataframe = object()
    calls = []
    def result(name, value):
        def call(*args, **kwargs): calls.append(name); return value
        return call
    with patch("fabricops_kit.pipeline.orchestrate_read.pipeline_read", result("read", {"dataframe": dataframe, "table_id": "source-id"})), patch("fabricops_kit.pipeline.orchestrate_read.check_freshness", result("freshness", {"status": "skipped"})), patch("fabricops_kit.pipeline.orchestrate_read.check_schema", result("schema", {"status": "passed"})), patch("fabricops_kit.pipeline.orchestrate_read.check_dq", result("dq", {"status": "passed"})), patch("fabricops_kit.pipeline.orchestrate_read.profile_table", result("profile", {"profile": object()})):
        actual = orchestrate_read(name="orders", store="Bronze", schema="demo", table_name="orders", verbose=False)
    assert calls == ["read", "freshness", "schema", "dq", "profile"]
    assert actual["dataframe"] is dataframe
    assert actual["table_id"] == "source-id"
    assert actual["orchestration_stages"][1]["status"] == "skipped"


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
        return_value={"status": "skipped"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_schema",
        return_value={"status": "skipped"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.check_dq",
        return_value={"status": "skipped"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_read.profile_table",
        return_value={"status": "skipped"},
    ):
        actual = orchestrate_read(
            name="history",
            store="Product",
            schema="demo",
            table_name="order_history",
        )

    assert "_reader_name" not in actual
    assert "      Physical read → read_warehouse_table" in capsys.readouterr().out


def test_orchestrate_read_attributes_failure_and_stops_later_stages():
    """Read failures retain cause and stop later stages."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read
    cause = ValueError("meaningful schema mismatch")
    with patch("fabricops_kit.pipeline.orchestrate_read.pipeline_read", return_value={"dataframe": object(), "table_id": "source-id"}), patch("fabricops_kit.pipeline.orchestrate_read.check_freshness", return_value={"status": "passed"}), patch("fabricops_kit.pipeline.orchestrate_read.check_schema", side_effect=cause), patch("fabricops_kit.pipeline.orchestrate_read.check_dq") as dq:
        with pytest.raises(RuntimeError, match="READ 'orders' failed during Schema") as raised:
            orchestrate_read(name="orders", store="Bronze", schema="demo", table_name="orders", verbose=False)
    assert raised.value.__cause__ is cause
    dq.assert_not_called()


def test_orchestrate_write_orders_stages_and_profiles_after_write():
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
        patch("fabricops_kit.pipeline.orchestrate_write.check_source_drift", effect("drift", {"status":"skipped"})),
        patch("fabricops_kit.pipeline.orchestrate_write.check_dq", effect("dq", {"status":"passed"})),
        patch("fabricops_kit.pipeline.orchestrate_write.check_guardrail_coverage", effect("coverage", {"status":"passed"})),
        patch("fabricops_kit.pipeline.orchestrate_write.pipeline_write", side_effect=effect("write", {"table_id":"target-id"})),
        patch("fabricops_kit.pipeline.orchestrate_write.profile_table", effect("profile", {"profile":object()})),
    ]
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6] as write, patches[7]:
        actual = orchestrate_write(dataframe, name="target", sources=[{"table_id":"source-id"}], store="Silver", schema="demo", table_name="target", write_mode="overwrite", verbose=False)
    assert calls == ["schema", "sensitive", "drift", "dq", "coverage", "write", "profile"]
    assert actual["published"] is True
    assert actual["table_id"] == "target-id"
    assert write.call_args.args[0] is prepared


def test_orchestrate_write_preserves_guardrail_failure_and_does_not_write():
    """Write failures retain the Guardrail cause and prevent publication."""
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write
    cause = RuntimeError("blocking DQ rule: completeness 96.7%")
    with patch("fabricops_kit.pipeline.orchestrate_write.resolve_table_id", return_value="target-id"), patch("fabricops_kit.pipeline.orchestrate_write.check_schema", return_value={"status":"passed"}), patch("fabricops_kit.pipeline.orchestrate_write.check_sensitive_data", return_value={"status":"passed", "dataframe":object()}), patch("fabricops_kit.pipeline.orchestrate_write.check_source_drift", return_value={"status":"passed"}), patch("fabricops_kit.pipeline.orchestrate_write.check_dq", side_effect=cause), patch("fabricops_kit.pipeline.orchestrate_write.pipeline_write") as write:
        with pytest.raises(RuntimeError, match="WRITE 'target' failed during Data Quality") as raised:
            orchestrate_write(object(), name="target", sources=[{"table_id":"source-id"}], store="Silver", schema="demo", table_name="target", write_mode="overwrite", verbose=False)
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
            orchestrate_read(
                name="orders",
                store="Bronze",
                schema="demo",
                table_name="orders",
            )

    output = capsys.readouterr().out
    assert "[3/5] Schema ... ✗ Failed" in output
    assert "[3/5] Schema ... ✓ Passed" not in output
    assert "Later stages did not run." in output


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


def test_validate_runs_enforce_guardrails_then_skips_write_and_profile():
    """Validate is the enforcement Guardrail path with publication omitted."""
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write

    dataframe, prepared = object(), object()
    calls = []

    def record(stage, result):
        def call(*args, **kwargs):
            calls.append(stage)
            return result

        return call

    contracts = {
        "tables": {"target-id": {"mode": "validate"}},
        "validate": Mock(side_effect=AssertionError("legacy validation callback called")),
    }
    with patch(
        "fabricops_kit.pipeline.orchestrate_write.resolve_table_id",
        return_value="target-id",
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_schema",
        record("schema", {"status": "passed"}),
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_sensitive_data",
        record("sensitive", {"status": "passed", "dataframe": prepared}),
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_source_drift",
        record("drift", {"status": "passed"}),
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_dq",
        record("dq", {"status": "passed"}),
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_guardrail_coverage",
        record("coverage", {"status": "passed"}),
    ), patch("fabricops_kit.pipeline.orchestrate_write.pipeline_write") as write, patch(
        "fabricops_kit.pipeline.orchestrate_write.profile_table"
    ) as profile:
        result = orchestrate_write(
            dataframe,
            name="target",
            sources=[{"table_id": "source-id"}],
            store="Silver",
            schema="demo",
            table_name="target",
            write_mode="overwrite",
            contracts=contracts,
            verbose=False,
        )

    assert calls == ["schema", "sensitive", "drift", "dq", "coverage"]
    assert result["published"] is False
    assert result["validation_passed"] is True
    assert [stage["stage"] for stage in result["orchestration_stages"]] == [
        "Schema",
        "Sensitive Data",
        "Source Drift",
        "Data Quality",
        "Guardrail Coverage",
    ]
    contracts["validate"].assert_not_called()
    write.assert_not_called()
    profile.assert_not_called()


def test_validate_guardrail_failure_matches_enforce_and_stops_publication(capsys):
    """Validate attributes the same blocking Guardrail and never publishes."""
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write

    cause = RuntimeError("blocking target Data Quality rule")
    contracts = {"tables": {"target-id": {"mode": "validate"}}}
    with patch(
        "fabricops_kit.pipeline.orchestrate_write.resolve_table_id",
        return_value="target-id",
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_schema",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_sensitive_data",
        return_value={"status": "passed", "dataframe": object()},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_source_drift",
        return_value={"status": "passed"},
    ), patch(
        "fabricops_kit.pipeline.orchestrate_write.check_dq",
        side_effect=cause,
    ), patch("fabricops_kit.pipeline.orchestrate_write.pipeline_write") as write:
        with pytest.raises(
            RuntimeError, match="WRITE 'target' failed during Data Quality"
        ) as raised:
            orchestrate_write(
                object(),
                name="target",
                sources=[{"table_id": "source-id"}],
                store="Silver",
                schema="demo",
                table_name="target",
                write_mode="overwrite",
                contracts=contracts,
            )

    output = capsys.readouterr().out
    assert "[4/5] Data Quality ... ✗ Failed" in output
    assert "[4/5] Data Quality ... ✓ Passed" not in output
    assert "Later stages did not run." in output
    assert raised.value.__cause__ is cause
    write.assert_not_called()
