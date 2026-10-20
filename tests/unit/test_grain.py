"""Grain ownership, exact contracts, evaluated rows, and continuation behavior."""

import importlib
import json
from unittest.mock import Mock

import pytest

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline.shared import contract_guardrail_rows, grain_check_core
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


@pytest.mark.parametrize("action,status,continuation", [("Warn", "warning", True), ("Block", "failed", False)])
def test_composite_duplicates_and_nulls(spark_session, action, status, continuation):
    """Repeated components are valid; repeated combinations and any null fail."""
    frame = spark_session.createDataFrame([(1, 1), (1, 2), (2, 1), (2, 1), (3, None)], "id long, version long")
    result = grain_check_core(frame, _rule(action=action), scope="write_prepared_input")
    assert result["status"] == status
    assert result["can_continue"] is continuation
    assert result["actual"] == {"total_count": 5, "duplicate_key": 2, "null_key": 1, "failed_key": 3}
    assert result["columns"] == ["id", "version"]


@pytest.mark.parametrize("columns", [[], ["id", "id"], ["missing"], [""], [" id"], "id"])
def test_invalid_keys_never_pass_even_empty_warn_input(spark_session, columns):
    """Missing or malformed configured keys block before empty-table success."""
    frame = spark_session.createDataFrame([], "id long, version long")
    result = grain_check_core(frame, _rule(columns, action="Warn"), scope="read_full")
    assert result["status"] == "failed"
    assert result["can_continue"] is False


def test_empty_input_and_blank_string_values(spark_session):
    """A valid empty input passes; blank strings are ordinary key values."""
    empty = spark_session.createDataFrame([], "id string, version long")
    assert grain_check_core(empty, _rule(), scope="read_full")["status"] == "passed"
    frame = spark_session.createDataFrame([("", 1), ("", 2)], "id string, version long")
    assert grain_check_core(frame, _rule(), scope="read_full")["status"] == "passed"


@pytest.mark.parametrize("active", [True, False])
def test_assembled_frozen_runtime_round_trip(active):
    """Inactive keys and descriptions survive assembly and freezing without active rules."""
    draft = {"contract_id": "c", "contract_version": 2, "table_id": "t", "environment_name": "dev", "status": "draft", "contract_payload_json": json.dumps({"table": {"processing": {"load_strategy": "append"}}})}
    rule = {**_rule(active=active), "contract_id": "c", "contract_version": 2, "environment_name": "dev"}
    payload, _warnings = contracts.assemble_contract_payload(draft=draft, environment_name="dev", catalogue_rows=[{"table_id": "t", "environment_name": "dev", "metadata_level": "table", "table_name": "history"}, *[
            {"table_id": "t", "environment_name": "dev", "metadata_level": "column", "column_id": name, "column_name": name, "data_type": "bigint"} for name in ("id", "version")]], enrichment_rows=[{"enrichment_id": "description", "contract_id": "c", "contract_version": 2, "environment_name": "dev", "enrichment_level": "table", "enrichment_type": "Grain", "value": "One row per version"}], guardrail_rows=[rule])
    frozen = contracts.freeze_contract_record(draft={**draft, "contract_payload_json": json.dumps(payload)}, audit={})
    frozen_payload = json.loads(frozen["contract_payload_json"])
    assert frozen_payload["guardrails"][0]["action"] == "Block"
    assert frozen_payload["guardrails"][0]["rule_parameters"] == {"columns": ["id", "version"]}
    assert frozen_payload["enrichment"]["table"][0]["value"] == "One row per version"
    runtime = contract_guardrail_rows(frozen, environment_name="dev", table_id="t")
    assert len(runtime) == int(active)
    if active:
        assert runtime[0]["guardrail_type"] == "grain"
        assert json.loads(runtime[0]["rule_parameters_json"]) == {"columns": ["id", "version"]}


def test_scd2_history_uses_version_aware_grain(spark_session):
    """History repeats business keys; Grain never rewrites strategy keys or filters history."""
    history = spark_session.createDataFrame([(1, 1), (1, 2), (2, 1)], ["id", "version"])
    assert grain_check_core(history, _rule(), scope="read_full")["status"] == "passed"
    assert grain_check_core(history, _rule(["id"]), scope="read_full")["status"] == "failed"


def test_incomplete_grain_preview_cannot_be_saved_frozen_or_enforced():
    """Editable previews retain unfinished keys without weakening authoritative validation."""
    draft = {"contract_id": "c", "contract_version": 1, "table_id": "t", "environment_name": "dev", "status": "draft",
             "contract_payload_json": json.dumps({"table": {"processing": {"load_strategy": "overwrite"}}})}
    tables = {
        "METADATA_DATA_CATALOGUE": [
            {"table_id": "t", "environment_name": "dev", "metadata_level": "table", "table_name": "orders"},
            {"table_id": "t", "environment_name": "dev", "metadata_level": "column", "column_id": "id", "column_name": "id", "data_type": "bigint"},
        ],
        "enrichment": [],
        "guardrails": [{**_rule([]), "contract_id": "c", "contract_version": 1, "environment_name": "dev"}],
    }
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contracts.assemble_contract_payload(draft=draft, catalogue_rows=tables["METADATA_DATA_CATALOGUE"], enrichment_rows=tables["enrichment"], guardrail_rows=tables["guardrails"], environment_name="dev")
    preview, _ = contracts.assemble_contract_payload(draft=draft, catalogue_rows=tables["METADATA_DATA_CATALOGUE"], enrichment_rows=tables["enrichment"], guardrail_rows=tables["guardrails"], environment_name="dev", allow_incomplete_grain=True)
    assert preview["guardrails"][0]["rule_parameters"]["columns"] == []
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contracts.save_contract_draft(draft=draft, payload=preview, config=object(), env="dev", spark_session=object())
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contracts.freeze_contract_record(draft={**draft, "contract_payload_json": json.dumps(preview)}, audit={})
    with pytest.raises(ValueError, match="Enforced Grain requires"):
        contract_guardrail_rows({"contract_payload": preview}, environment_name="dev", table_id="t")


@pytest.mark.parametrize("mode,action", [("testing", "Block"), ("live", "Block"), ("live", "Warn")])
def test_grain_plan_guardrails_and_continuation(contract_runtime, spark_session, monkeypatch, mode, action):
    """Exact Grain outcomes govern Live continuation and remain in memory in Testing."""
    make, rows, spies, _ = contract_runtime
    rows.extend([frozen(SOURCE_ID, active=mode == "live"), frozen(TARGET_ID, active=mode == "live")])
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
    if mode == "live":
        monkeypatch.setattr(module, "pipeline_write", publish)
        monkeypatch.setattr(module, "profile_table", Mock(return_value={"row_count": 2}))
    if mode == "live" and action == "Block":
        with pytest.raises(RuntimeError, match="during Grain"):
            write(plan, source, spark_session, dataframe=frame)
        publish.assert_not_called()
    else:
        result = write(plan, source, spark_session, dataframe=frame)
        assert result["grain_result"]["validation_scope"] == "write_prepared_input"
        assert result["grain_result"]["can_continue"] is (action == "Warn")
        assert result["published"] is (mode == "live")
    assert any(row["guardrail_type"] == "grain" for row in plan.results)
    if mode == "testing":
        assert all(spy.call_count == 0 for spy in spies.values())
