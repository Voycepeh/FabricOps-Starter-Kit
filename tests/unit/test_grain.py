"""Grain ownership, exact contracts, evaluated rows, and continuation behavior."""

import importlib
import json
from unittest.mock import Mock

import pytest

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline.shared import contract_guardrail_rows, _evaluate_dq_rules
from tests.unit.test_contract_orchestration import runtime as grain_runtime, SOURCE_ID, TARGET_ID, frozen, read, write


@pytest.fixture
def contract_runtime(request):
    """Use the real contract orchestration metadata boundary fixture."""
    return request.getfixturevalue("grain_runtime")


def _rule(columns=None, action="Block", active=True):
    return {
        "guardrail_rule_id": "grain", "guardrail_version": 1, "guardrail_type": "grain",
        "rule_type": "uniqueness", "rule_id": "grain", "column_id": "", "action": action,
        "is_active": active, "rule_parameters_json": json.dumps({"columns": columns if columns is not None else ["id", "version"]}),
    }


@pytest.mark.parametrize("severity,status", [("warning", "warning"), ("error", "failed")])
def test_composite_duplicates_and_nulls(spark_session, severity, status):
    """Managed Grain uses DQ uniqueness with a strict non-null composite key."""
    frame = spark_session.createDataFrame([(1, 1), (1, 2), (2, 1), (2, 1), (3, None)], "id long, version long")
    result = _evaluate_dq_rules(frame, "history", [{"rule_id": "grain", "rule_type": "uniqueness",
        "columns": ["id", "version"], "require_non_null": True, "maximum_failure_percent": 0, "severity": severity}])
    assert len(result["checks"]) == 1
    assert result["checks"][0]["status"] == status
    assert result["checks"][0]["failed_count"] == 3
    assert result["failed_row_count"] == 3


def test_empty_input_and_blank_string_values(spark_session):
    """A valid empty input passes; blank strings are ordinary key values."""
    rule = {"rule_id": "grain", "rule_type": "uniqueness", "columns": ["id", "version"],
            "require_non_null": True, "maximum_failure_percent": 0, "severity": "error"}
    for rows in ([], [("", 1), ("", 2)]):
        frame = spark_session.createDataFrame(rows, "id string, version long")
        assert _evaluate_dq_rules(frame, "history", [rule])["checks"][0]["status"] == "passed"


@pytest.mark.parametrize("active", [True, False])
def test_assembled_frozen_runtime_round_trip(active):
    """Inactive keys and descriptions survive assembly and freezing without active rules."""
    draft = {"contract_id": "c", "contract_version": 2, "table_id": "t", "workspace_id": "dev", "status": "draft", "contract_payload_json": json.dumps({"table": {"processing": {"load_strategy": "append_all"}}})}
    rule = {**_rule(active=active), "contract_id": "c", "contract_version": 2, "workspace_id": "dev"}
    payload, _warnings = contracts.assemble_contract_payload(draft=draft, workspace_id="dev", catalogue_rows=[{"table_id": "t", "workspace_id": "dev", "metadata_level": "table", "table_name": "history"}, *[
            {"table_id": "t", "workspace_id": "dev", "metadata_level": "column", "column_id": name, "column_name": name, "data_type": "bigint"} for name in ("id", "version")]], enrichment_rows=[{"enrichment_id": "description", "contract_id": "c", "contract_version": 2, "workspace_id": "dev", "enrichment_level": "table", "enrichment_type": "Grain", "value": "One row per version"}], guardrail_rows=[rule])
    frozen = contracts.freeze_contract_record(draft={**draft, "contract_payload_json": json.dumps(payload)}, audit={})
    frozen_payload = json.loads(frozen["contract_payload_json"])
    assert frozen_payload["guardrails"][0]["action"] == "Block"
    assert frozen_payload["guardrails"][0]["rule_parameters"] == {"columns": ["id", "version"]}
    assert frozen_payload["enrichment"]["table"][0]["value"] == "One row per version"
    runtime = contract_guardrail_rows(frozen, workspace_id="dev", table_id="t")
    runtime = [row for row in runtime if row.get("managed_by") == "grain"]
    assert len(runtime) == int(active)
    if active:
        assert runtime[0]["guardrail_type"] == "data_quality"
        assert json.loads(runtime[0]["rule_parameters_json"]) == {"columns": ["id", "version"], "require_non_null": True, "maximum_failure_percent": 0}


def test_incomplete_grain_preview_cannot_be_saved_frozen_or_enforced():
    """Editable previews retain unfinished keys without weakening authoritative validation."""
    draft = {"contract_id": "c", "contract_version": 1, "table_id": "t", "workspace_id": "dev", "status": "draft",
             "contract_payload_json": json.dumps({"table": {"processing": {"load_strategy": "overwrite"}}})}
    tables = {
        "METADATA_DATA_CATALOGUE": [
            {"table_id": "t", "workspace_id": "dev", "metadata_level": "table", "table_name": "orders"},
            {"table_id": "t", "workspace_id": "dev", "metadata_level": "column", "column_id": "id", "column_name": "id", "data_type": "bigint"},
        ],
        "enrichment": [],
        "guardrails": [{**_rule([]), "contract_id": "c", "contract_version": 1, "workspace_id": "dev"}],
    }
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contracts.assemble_contract_payload(draft=draft, catalogue_rows=tables["METADATA_DATA_CATALOGUE"], enrichment_rows=tables["enrichment"], guardrail_rows=tables["guardrails"], workspace_id="dev")
    preview, _ = contracts.assemble_contract_payload(draft=draft, catalogue_rows=tables["METADATA_DATA_CATALOGUE"], enrichment_rows=tables["enrichment"], guardrail_rows=tables["guardrails"], workspace_id="dev", allow_incomplete_grain=True)
    assert preview["guardrails"][0]["rule_parameters"]["columns"] == []
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contracts.save_contract_draft(draft=draft, payload=preview, config=object(), active_workspace_id="dev", spark_session=object())
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contracts.freeze_contract_record(draft={**draft, "contract_payload_json": json.dumps(preview)}, audit={})
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contract_guardrail_rows({**preview["contract"], "contract_payload": preview}, workspace_id="dev", table_id="t")


@pytest.mark.parametrize("mode,action", [("dry_run", "Block"), ("governed", "Block"), ("governed", "Warn")])
def test_grain_plan_guardrails_and_continuation(contract_runtime, spark_session, monkeypatch, mode, action):
    """Exact Grain outcomes govern Live continuation and remain in memory in Testing."""
    make, rows, spies, _ = contract_runtime
    rows.extend([frozen(SOURCE_ID, active=mode == "governed"), frozen(TARGET_ID, active=mode == "governed")])
    payload = json.loads(rows[1]["contract_payload_json"])
    rule = _rule(["id"], action=action)
    rule["rule_parameters"] = json.loads(rule.pop("rule_parameters_json"))
    payload["guardrails"] = [rule]
    rows[1]["contract_payload_json"] = json.dumps(payload)
    plan = make(mode, contracted=True)
    source = read(plan, spark_session)
    frame = spark_session.createDataFrame([(1,), (1,)], "id long")
    # Grain is the actual evaluator; isolate downstream Fabric publication after Warn.
    module = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    publish = Mock(return_value={"table_id": TARGET_ID, "strategy": "overwrite"})
    if mode == "governed":
        monkeypatch.setattr(module, "pipeline_write", publish)
        monkeypatch.setattr(module, "schedule_table_profiling", Mock(return_value={"row_count": 2}))
    if mode == "governed" and action == "Block":
        with pytest.raises(RuntimeError, match="during Data Quality"):
            write(plan, source, spark_session, dataframe=frame)
        publish.assert_not_called()
    else:
        result = write(plan, source, spark_session, dataframe=frame)
        assert result["dq_result"]["can_continue"] is (action == "Warn")
        assert result["published"] is (mode == "governed")
    results = [row for row in plan.results if row["guardrail_rule_id"] == "grain"]
    assert len(results) == 1
    assert results[0]["guardrail_type"] == "data_quality"
    if mode == "dry_run":
        from tests.unit.test_contract_orchestration import assert_testing_mutations_are_diagnostics_only
        assert_testing_mutations_are_diagnostics_only(spies)


def test_managed_grain_rejects_duplicate_authored_uniqueness():
    """The same selected key cannot execute and count as a second DQ rule."""
    payload = {"table": {"columns": [{"column_name": "id"}]}, "guardrails": [
        {"guardrail_type": "grain", "rule_type": "uniqueness", "rule_parameters": {"columns": ["id"]}, "action": "Block"},
        {"guardrail_type": "data_quality", "rule_type": "uniqueness", "rule_parameters": {"columns": ["id"]}, "action": "Warn"},
    ]}
    with pytest.raises(ValueError, match="duplicate DQ rule"):
        contracts.validate_grain_contract(payload)
    payload["guardrails"][1]["is_active"] = False
    contracts.validate_grain_contract(payload)
