"""Contract selection, real stage evaluation, evidence, and dynamic reporting."""

import importlib
import json
from collections import Counter
from unittest.mock import Mock

import pytest

from fabricops_kit import orchestrate_read, orchestrate_write
from fabricops_kit.pipeline import shared
from fabricops_kit.widgets.widget_activate_data_contract import _latest_validation
from tests.helpers import framework_config
from tests.unit.test_data_contract_resolution import RecordingFrame
from tests.unit.test_widget_select_data_contract import _render

read_module = importlib.import_module("fabricops_kit.pipeline.orchestrate_read")
write_module = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
schema_module = importlib.import_module("fabricops_kit.pipeline.check_schema")
coverage_module = importlib.import_module("fabricops_kit.pipeline.check_guardrail_coverage")


@pytest.fixture
def contract_runtime(monkeypatch):
    """Keep widget selection, exact resolution, evaluators and evidence conversion real."""
    config = framework_config()
    audit = {"_activity_id": "validation-run"}
    writes = []
    reads = Counter()
    rule_specs = [
        ("schema", "required_columns", "", {"required_columns": ["id-column"]}),
        ("sensitive_data", "mask", "email-column", {"scope": "column", "treatment": "mask", "preserve_start": 0, "preserve_end": 0, "mask_character": "*"}),
        ("data_quality", "completeness", "id-column", {"columns": ["id"], "maximum_missing_percent": 0, "treat_blank_as_missing": False}),
    ]
    payload = {
        "contract": {"contract_id": "contract-target", "contract_version": 2},
        "table": {"table_id": "target", "columns": [
            {"column_id": "id-column", "column_name": "id", "data_type": "bigint"},
            {"column_id": "email-column", "column_name": "email", "data_type": "string"}],
            "processing": {"load_strategy": "overwrite"}},
        "guardrails": [{"guardrail_rule_id": kind, "guardrail_version": 1,
            "contract_id": "contract-target", "contract_version": 2, "guardrail_type": kind,
            "rule_id": kind, "rule_type": rule_type, "column_id": column,
            "rule_parameters": parameters, "action": "Block", "is_active": True}
            for kind, rule_type, column, parameters in rule_specs],
    }
    frozen = {"contract_id": "contract-target", "contract_version": 2, "table_id": "target",
              "environment_name": "dev", "status": "frozen", "is_active": False,
              "contract_payload_json": json.dumps(payload)}
    context, selection = _render(monkeypatch, [frozen], pairs=[("Target", "target")])
    context["config"] = config
    selection["set_mode"]("target", "validate", "contract-target", 2)
    assert "target" not in context["data_contract_overrides"]
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (config, "dev", context))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **_kwargs: audit)
    monkeypatch.setattr(coverage_module, "build_runtime_audit_fields", lambda **_kwargs: audit)
    monkeypatch.setattr(coverage_module, "_current_activity_results", lambda **_kwargs: writes)
    monkeypatch.setattr(write_module, "resolve_table_id", lambda **_kwargs: "target")
    monkeypatch.setattr(read_module, "resolve_table_id", lambda **_kwargs: "target")
    monkeypatch.setattr(schema_module, "resolve_lakehouse_table_location", lambda *_args: ("target", "dbo", "unused"))
    catalogue = [{"table_id": "target", "metadata_level": "table", "column_id": "",
                  "environment_name": "dev", "store_type": "lakehouse", "layer": "Silver",
                  "table_name": "target", "schema_name": "dbo"}]

    def read(table, **_kwargs):
        reads[table] += 1
        return RecordingFrame([frozen] if table == "METADATA_DATA_CONTRACT" else catalogue)

    def persist(frame, table, **_kwargs):
        assert table == "METADATA_GUARDRAIL_RESULTS"
        writes.extend(row.asDict(recursive=True) for row in frame.collect())

    monkeypatch.setattr(shared, "read_lakehouse_table", read)
    monkeypatch.setattr(shared, "write_lakehouse_table", persist)
    monkeypatch.setattr(write_module, "pipeline_write", Mock(side_effect=AssertionError("Validate must not publish")))
    return selection, context, payload, frozen, writes, reads


def test_widget_candidate_is_evaluated_and_produces_activation_evidence(contract_runtime, spark_session, capsys):
    """Validate resolves the chosen version despite the selector clearing its override."""
    selection, context, _payload, _frozen, writes, reads = contract_runtime
    frame = spark_session.createDataFrame([(1, "raw@example.test")], ["id", "email"])
    result = orchestrate_write(frame, sources=[], store="Silver", schema="dbo", table_name="target",
                              write_mode="overwrite", contracts=selection, spark_session=spark_session)
    assert result["validation_passed"] is True
    assert result["published"] is False
    assert result["dataframe"].first().email == "****************"
    assert len(writes) == 4
    assert writes[-1]["rule_type"] == "contract_validation"
    assert {row["execution_type"] for row in writes} == {"validate"}
    assert {row["contract_id"] for row in writes} == {"contract-target"}
    assert {row["contract_version"] for row in writes} == {2}
    assert all(row["can_continue"] for row in writes)
    assert _latest_validation(writes, contract_id="contract-target", contract_version=2, environment_name="dev")["validated"]
    assert reads == {"METADATA_DATA_CONTRACT": 1, "METADATA_DATA_CATALOGUE": 1}
    assert "target" not in context["data_contract_overrides"]
    output = capsys.readouterr().out
    assert "Checking Schema, Sensitive Data, Data Quality" in output
    assert "Skipped" not in output
    assert "Freshness" not in output
    assert "Source Drift" not in output


def test_processing_mismatch_cannot_produce_activation_evidence(contract_runtime, spark_session):
    """Real Guardrail success cannot validate an incompatible publication strategy."""
    selection, _context, _payload, _frozen, writes, _reads = contract_runtime
    frame = spark_session.createDataFrame([(1, "raw@example.test")], ["id", "email"])
    with pytest.raises(RuntimeError, match="failed during Processing"):
        orchestrate_write(frame, sources=[], store="Silver", schema="dbo", table_name="target",
                          write_mode="append", contracts=selection, spark_session=spark_session, verbose=False)
    assert writes and all(row["can_continue"] for row in writes)
    assert not any(row["rule_type"] == "contract_validation" for row in writes)
    assert not _latest_validation(writes, contract_id="contract-target", contract_version=2, environment_name="dev")["validated"]


def test_validate_missing_required_column_persists_failure_and_stops(contract_runtime, spark_session):
    """Real Schema failure cannot become a successful validation or activation."""
    selection, _context, _payload, _frozen, writes, _reads = contract_runtime
    frame = spark_session.createDataFrame([("raw@example.test",)], ["email"])
    with pytest.raises(RuntimeError, match="failed during Schema"):
        orchestrate_write(frame, sources=[], store="Silver", schema="dbo", table_name="target",
                          write_mode="overwrite", contracts=selection, spark_session=spark_session, verbose=False)
    assert len(writes) == 1
    assert writes[0]["execution_type"] == "validate"
    assert writes[0]["status"] == "failed"
    assert writes[0]["can_continue"] is False
    assert not _latest_validation(writes, contract_id="contract-target", contract_version=2, environment_name="dev")["validated"]


def test_schema_only_contract_prints_only_applicable_check(contract_runtime, spark_session, capsys):
    """A partial Guardrail bundle does not call or print unrelated stages."""
    selection, _context, payload, frozen, writes, reads = contract_runtime
    payload["guardrails"] = payload["guardrails"][:1]
    frozen["contract_payload_json"] = json.dumps(payload)
    frame = spark_session.createDataFrame([(1,)], ["id"])
    result = orchestrate_write(frame, sources=[], store="Silver", schema="dbo", table_name="target",
                              write_mode="overwrite", contracts=selection, spark_session=spark_session)
    assert [stage["stage"] for stage in result["orchestration_stages"]] == ["Schema", "Guardrail Coverage", "Processing"]
    assert result["sensitive_result"]["status"] == result["dq_result"]["status"] == "skipped"
    output = capsys.readouterr().out
    assert "Checking Schema." in output
    assert all(name not in output for name in ["Sensitive Data", "Data Quality", "Freshness", "Skipped"])
    assert len(writes) == 2
    assert writes[-1]["guardrail_type"] == "guardrail_coverage"
    assert reads["METADATA_DATA_CONTRACT"] == 1


@pytest.mark.parametrize("operation", ["read", "write"])
def test_contract_free_run_prints_one_decision_and_no_check_skips(monkeypatch, spark_session, capsys, operation):
    """Development baseline avoids Guardrail metadata reads and skip-row output."""
    context = {"config": framework_config(), "env": "dev"}
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (context["config"], "dev", context))
    monkeypatch.setattr(shared, "read_lakehouse_table", Mock(side_effect=AssertionError("No Guardrail metadata needed")))
    frame = spark_session.createDataFrame([(1,)], ["id"])
    module = read_module if operation == "read" else write_module
    monkeypatch.setattr(module, "resolve_table_id", lambda **_kwargs: "target")
    monkeypatch.setattr(module, "profile_table", lambda **_kwargs: {"row_count": 1})
    if operation == "read":
        monkeypatch.setattr(module, "pipeline_read", lambda **_kwargs: {"table_id": "target", "dataframe": frame})
        result = orchestrate_read(store="Silver", schema="dbo", table_name="target", spark_session=spark_session)
        expected = ["Read", "Profile"]
    else:
        monkeypatch.setattr(module, "pipeline_write", lambda *_args, **_kwargs: {"table_id": "target"})
        result = orchestrate_write(frame, sources=[], store="Silver", schema="dbo", table_name="target",
                                   write_mode="overwrite", spark_session=spark_session)
        expected = ["Write", "Profile"]
    assert [stage["stage"] for stage in result["orchestration_stages"]] == expected
    output = capsys.readouterr().out
    assert output.count("No Data Contract selected") == 1
    assert "Skipped" not in output
    assert all(name not in output for name in ["Schema", "Freshness", "Data Quality", "Sensitive Data", "Guardrail Coverage"])


def test_validate_requires_exact_candidate(monkeypatch):
    """An incomplete selection cannot silently return successful validation."""
    config = framework_config()
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (config, "dev", {}))
    with pytest.raises(ValueError, match="exact frozen"):
        shared.prepare_pipeline_execution(["target"], contracts={"tables": {"target": {"mode": "validate"}}})


def test_repeated_authored_dq_type_keeps_each_rules_own_persisted_outcome(contract_runtime, spark_session):
    """Widget rules may share a rule_id/type while identifying different columns."""
    selection, _context, payload, frozen, writes, _reads = contract_runtime
    first = payload["guardrails"][-1]
    first["rule_id"] = "completeness"
    second = {**first, "guardrail_rule_id": "email-completeness", "column_id": "email-column",
              "rule_parameters": {**first["rule_parameters"], "columns": ["email"]}}
    payload["guardrails"].append(second)
    frozen["contract_payload_json"] = json.dumps(payload)
    frame = spark_session.createDataFrame([(None, "raw@example.test")], "id long, email string")
    with pytest.raises(RuntimeError, match="failed during Data Quality"):
        orchestrate_write(frame, sources=[], store="Silver", schema="dbo", table_name="target",
                          write_mode="overwrite", contracts=selection, spark_session=spark_session, verbose=False)
    results = {row["guardrail_rule_id"]: row for row in writes if row["guardrail_type"] == "data_quality"}
    assert results["data_quality"]["status"] == "failed"
    assert results["email-completeness"]["status"] == "passed"
    assert len({row["guardrail_result_id"] for row in results.values()}) == 2


def test_processing_reuses_the_same_frozen_contract_as_guardrails(contract_runtime):
    """The physical Write processing path must not resolve a second snapshot."""
    selection, _context, _payload, _frozen, _writes, reads = contract_runtime
    context = shared.prepare_pipeline_execution(["target"], contracts=selection)
    for _ in range(2):
        processing = shared.resolve_table_processing_definition(context["config"], "dev", "target",
            context=context, authored_processing={"load_strategy": "overwrite"})
        assert processing["contract_id"] == "contract-target"
        assert processing["contract_version"] == 2
    assert reads == {"METADATA_DATA_CONTRACT": 1}
