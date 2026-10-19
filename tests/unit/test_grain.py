"""Grain ownership, exact contracts, evaluated rows, and continuation behavior."""

import importlib
import json
from unittest.mock import Mock

import pytest

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline.shared import contract_guardrail_rows, grain_check_core
from tests.unit.test_contract_orchestration import contract_runtime as grain_runtime


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
    payload, _warnings = contracts.assemble_contract_payload(draft=draft, environment_name="dev", tables={
        "METADATA_DATA_CATALOGUE": [{"table_id": "t", "environment_name": "dev", "metadata_level": "table", "table_name": "history"}, *[
            {"table_id": "t", "environment_name": "dev", "metadata_level": "column", "column_id": name, "column_name": name, "data_type": "bigint"} for name in ("id", "version")]],
        "METADATA_ENRICHMENT": [{"enrichment_id": "description", "contract_id": "c", "contract_version": 2, "environment_name": "dev", "enrichment_level": "table", "enrichment_type": "Grain", "value": "One row per version"}],
        "METADATA_GUARDRAIL": [rule],
    })
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


def _grain_contract(runtime, action="Block", active=True):
    _selection, _context, payload, frozen, _writes, _reads = runtime
    rule = _rule(["id"], action=action, active=active)
    rule["rule_parameters"] = json.loads(rule.pop("rule_parameters_json"))
    payload["guardrails"] = [rule]
    frozen["contract_payload_json"] = json.dumps(payload)


@pytest.mark.parametrize("strategy", ["overwrite", "append", "scd1", "scd2"])
@pytest.mark.parametrize("action,active", [("Block", False), ("Warn", True), ("Block", True)])
def test_write_grain_independent_of_dq_and_continuation(contract_runtime, spark_session, monkeypatch, strategy, action, active):
    """Every strategy validates prepared input, records exact-version results, and gates continuation."""
    selection, _context, _payload, _frozen, writes, _reads = contract_runtime
    _grain_contract(contract_runtime, action, active)
    module = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    coverage = Mock(return_value={"status": "passed", "can_continue": True})
    monkeypatch.setattr(module, "check_guardrail_coverage", coverage)
    frame = spark_session.createDataFrame([(1, "a"), (1, "b")], ["id", "email"])
    args = dict(dataframe=frame, sources=[], store="Silver", schema="dbo", table_name="target", write_mode=strategy, contracts=selection, spark_session=spark_session, verbose=False)
    if active and action == "Block":
        with pytest.raises(RuntimeError, match="during Grain"):
            module.orchestrate_write(**args)
        coverage.assert_not_called()
    else:
        result = module.orchestrate_write(**args)
        assert result["grain_result"]["status"] == ("warning" if active else "skipped")
        assert result["dq_result"]["status"] == "skipped"
        coverage.assert_called_once()
    assert len(writes) == int(active)
    if active:
        assert writes[0]["guardrail_type"] == "grain"
        assert writes[0]["execution_type"] == "validate"
        assert writes[0]["contract_id"] == "contract-target"
        assert writes[0]["contract_version"] == 2
        assert json.loads(writes[0]["result_payload_json"])["validation_scope"] == "write_prepared_input"


@pytest.mark.parametrize("read_mode", ["full", "incremental"])
@pytest.mark.parametrize("action", ["Warn", "Block"])
def test_read_grain_gates_profile_and_return(contract_runtime, spark_session, monkeypatch, read_mode, action):
    """Read records Grain evidence and stops before Profile on Block."""
    _grain_contract(contract_runtime, action)
    contract_runtime[1]["data_contract_overrides"]["target"] = {"contract_id": "contract-target", "contract_version": 2}
    module = importlib.import_module("fabricops_kit.pipeline.orchestrate_read")
    frame = spark_session.createDataFrame([(1,), (1,)], ["id"])
    monkeypatch.setattr(module, "pipeline_read", lambda **_kw: {"table_id": "target", "dataframe": frame})
    profile = Mock(return_value={"row_count": 2})
    monkeypatch.setattr(module, "profile_table", profile)
    if action == "Block":
        with pytest.raises(RuntimeError, match="during Grain"):
            module.orchestrate_read(store="Silver", schema="dbo", table_name="target", read_mode=read_mode, spark_session=spark_session, verbose=False)
        profile.assert_not_called()
    else:
        result = module.orchestrate_read(store="Silver", schema="dbo", table_name="target", read_mode=read_mode, spark_session=spark_session, verbose=False)
        assert result["grain_result"]["validation_scope"] == ("read_full" if read_mode == "full" else "read_incremental_batch")
        assert result["dq_result"]["status"] == "skipped"
        assert profile.call_count == int(read_mode == "full")


def test_scd2_history_uses_version_aware_grain(spark_session):
    """History repeats business keys; Grain never rewrites strategy keys or filters history."""
    history = spark_session.createDataFrame([(1, 1), (1, 2), (2, 1)], ["id", "version"])
    assert grain_check_core(history, _rule(), scope="read_full")["status"] == "passed"
    assert grain_check_core(history, _rule(["id"]), scope="read_full")["status"] == "failed"


@pytest.mark.parametrize("action", ["Warn", "Block"])
def test_enforced_write_continuation(contract_runtime, spark_session, monkeypatch, action):
    """Warn reaches Write; Block stops publication after recording the Grain outcome."""
    _grain_contract(contract_runtime, action)
    selection, _context, _payload, frozen, writes, _reads = contract_runtime
    frozen["is_active"] = True
    selection["tables"]["target"]["mode"] = "enforce"
    module = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    publish = Mock(return_value={"table_id": "target", "strategy": "append"})
    monkeypatch.setattr(module, "pipeline_write", publish)
    monkeypatch.setattr(module, "profile_table", Mock(return_value={"row_count": 2}))
    monkeypatch.setattr(module, "check_guardrail_coverage", Mock(return_value={"can_continue": True}))
    frame = spark_session.createDataFrame([(1,), (1,)], ["id"])
    args = dict(sources=[], store="Silver", schema="dbo", table_name="target", write_mode="append", contracts=selection, spark_session=spark_session, verbose=False)
    if action == "Block":
        with pytest.raises(RuntimeError, match="during Grain"):
            module.orchestrate_write(frame, **args)
        publish.assert_not_called()
    else:
        result = module.orchestrate_write(frame, **args)
        assert result["grain_result"]["status"] == "warning"
        publish.assert_called_once()
    assert len(writes) == 1
    assert writes[0]["execution_type"] == "enforce"


def test_missing_prepared_key_records_failure_even_warn(contract_runtime, spark_session):
    """A key removed by treatment cannot silently pass or produce empty success."""
    _grain_contract(contract_runtime, "Warn")
    selection, _context, payload, frozen, writes, _reads = contract_runtime
    payload["guardrails"].append({"guardrail_rule_id": "remove-key", "guardrail_version": 1,
        "guardrail_type": "sensitive_data", "rule_type": "remove", "column_id": "id-column",
        "rule_parameters": {"scope": "column", "treatment": "remove"}, "action": "Block", "is_active": True})
    frozen["contract_payload_json"] = json.dumps(payload)
    module = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    frame = spark_session.createDataFrame([(1, "example")], "id long, email string")
    with pytest.raises(RuntimeError, match="Grain key columns are missing"):
        module.orchestrate_write(frame, sources=[], store="Silver", schema="dbo", table_name="target", write_mode="append", contracts=selection, spark_session=spark_session, verbose=False)
    assert [row["guardrail_type"] for row in writes] == ["sensitive_data", "grain"]
    assert writes[-1]["can_continue"] is False
    assert writes[-1]["status"] == "failed"
