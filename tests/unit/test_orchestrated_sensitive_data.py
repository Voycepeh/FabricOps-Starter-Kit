"""Sensitive Data treatment is enforced by the public Write workflow."""

import importlib
import json
from unittest.mock import Mock

import pytest

from fabricops_kit import orchestrate_write
from tests.helpers import execution_plan_stub, execution_context_stub
from fabricops_kit.pipeline import shared
from tests.helpers import run_pipeline_operation

write_module = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
sensitive_module = importlib.import_module("fabricops_kit.pipeline.check_sensitive_data")


@pytest.fixture
def write_workflow(monkeypatch):
    """Keep the treatment/evidence path real while isolating physical publication."""
    identity = {"table_id": "target-id", "table_name": "customers", "store_type": "lakehouse", "store": "Silver", "schema": "dbo"}
    monkeypatch.setattr(write_module, "resolve_table_id", lambda **_kwargs: "target-id")
    monkeypatch.setattr(write_module, "check_schema", lambda *_args, **_kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(write_module, "skip_table_profiling", lambda *args, **kwargs: {"status": "skipped"})
    later = {}
    for name in ("check_dq", "pipeline_write", "schedule_table_profiling"):
        later[name] = Mock(return_value={"status": "passed", "can_continue": True, "table_id": "target-id"})
        monkeypatch.setattr(write_module, name, later[name])
    monkeypatch.setattr(sensitive_module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(sensitive_module, "resolve_pipeline_data_contract", lambda *_args, **_kwargs: {"contract_id": "contract", "contract_version": 1})
    monkeypatch.setattr(sensitive_module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: identity)
    context = {"config": object(), "env": "dev", **execution_context_stub({"target-id": {"contract_id": "contract", "contract_version": 1, "contract_payload_json": "{}"}}, {"target-id": [{"guardrail_type": kind} for kind in ("schema", "sensitive_data", "data_quality")]})}
    def prepare(*args, **kwargs):
        context["execution_plan"] = kwargs["execution_plan"]
        return context
    monkeypatch.setattr(write_module, "prepare_pipeline_execution", prepare)
    evidence = []
    monkeypatch.setattr(shared, "write_guardrail_result_row", lambda **kwargs: evidence.append(kwargs["result"]))
    return evidence, later


@pytest.mark.parametrize("mode", ["testing", "live"])
@pytest.mark.parametrize("saved_action", ["Warn", "Block"])
def test_treatment_failure_blocks_write_after_persisting_outcome(monkeypatch, spark_session, write_workflow, mode, saved_action):
    """A missing treatment column cannot reach DQ or publication in either mode."""
    evidence, later = write_workflow
    rule = {
        "guardrail_rule_id": "sensitive-email", "guardrail_version": 1,
        "contract_id": "contract", "contract_version": 1,
        "guardrail_type": "sensitive_data", "column_id": "email-id", "column_name": "missing-email",
        "rule_parameters_json": json.dumps({"scope": "column", "treatment": "remove"}),
        "action": saved_action, "is_active": True,
    }
    monkeypatch.setattr(sensitive_module, "load_table_guardrail_rules", lambda *_args, **_kwargs: [rule])
    frame = spark_session.createDataFrame([(1, "raw@example.test")], ["id", "email"])
    def run():
        return run_pipeline_operation(orchestrate_write,
            frame, sources=[], store="Silver", schema="dbo", table_name="customers", write_mode="overwrite",
            plan=execution_plan_stub(mode), spark_session=spark_session, verbose=False,
        )
    if mode == "live":
        with pytest.raises(RuntimeError, match="failed during Sensitive Data"):
            run()
        for stage in later.values():
            stage.assert_not_called()
    else:
        result = run()
        assert not result["published"] and not result["validation_passed"]
    assert len(evidence) == 1
    assert evidence[0]["status"] == "failed"
    assert evidence[0]["can_continue"] is False
    assert evidence[0]["action"] == "Block"
    assert evidence[0]["severity"] == "blocking"
    assert "raw@example.test" not in json.dumps(evidence)


@pytest.mark.parametrize("mode", ["testing", "live"])
def test_token_mapping_reuse_and_treated_write_input(monkeypatch, spark_session, write_workflow, mode):
    """The public orchestrator retains established tokens and returns caller-owned mappings."""
    evidence, later = write_workflow
    rule = {
        "guardrail_rule_id": "sensitive-email", "guardrail_version": 1,
        "contract_id": "contract", "contract_version": 1,
        "guardrail_type": "sensitive_data", "column_id": "email-id", "column_name": "email",
        "rule_parameters_json": json.dumps({"scope": "column", "treatment": "tokenize"}),
        "action": "Block", "is_active": True,
    }
    monkeypatch.setattr(sensitive_module, "load_table_guardrail_rules", lambda *_args, **_kwargs: [rule])
    frame = spark_session.createDataFrame([(1, "raw@example.test")], ["id", "email"])
    existing = spark_session.createDataFrame(
        [("target-id", "email-id", "raw@example.test", "established-token")],
        ["table_id", "column_id", "original_value", "token_value"],
    )
    result = run_pipeline_operation(orchestrate_write,
        frame, sources=[], store="Silver", schema="dbo", table_name="customers", write_mode="overwrite",
        existing_mapping=existing, plan=execution_plan_stub(mode), spark_session=spark_session, verbose=False,
    )
    assert result["dataframe"].first().email == "established-token"
    assert result["sensitive_result"]["support_mapping"].first().original_value == "raw@example.test"
    assert result["published"] is (mode == "live")
    assert later["check_dq"].call_args.args[0] is result["dataframe"]
    if mode == "live":
        assert later["pipeline_write"].call_args.args[0] is result["dataframe"]
    else:
        assert later["pipeline_write"].call_args.args[0] is result["dataframe"]
    assert evidence[0]["status"] == "passed"
    assert "raw@example.test" not in json.dumps(evidence)


def test_frozen_widget_rule_materializes_for_internal_schema_stage(spark_session):
    """Widget snapshots become Spark rules without unused all-null severity fields."""
    from fabricops_kit.data_contract import shared as contracts

    draft = {"contract_id": "contract", "contract_version": 1, "table_id": "target-id", "status": "draft",
             "contract_payload_json": json.dumps({"table": {"processing": {"load_strategy": "overwrite"}}})}
    rule = {"guardrail_rule_id": "schema", "guardrail_version": 1, "contract_id": "contract", "contract_version": 1,
            "environment_name": "dev", "column_id": "", "guardrail_type": "schema", "rule_id": "required_columns",
            "rule_type": "required_columns", "rule_parameters_json": '{"required_columns":["email-id"]}', "action": "Block"}
    payload, _warnings = contracts.assemble_contract_payload(
        draft=draft, environment_name="dev", catalogue_rows=[
                {"table_id": "target-id", "metadata_level": "table", "environment_name": "dev"},
                {"table_id": "target-id", "metadata_level": "column", "environment_name": "dev",
                 "column_id": "email-id", "column_name": "email", "data_type": "string"},
            ], enrichment_rows=[], guardrail_rows=[rule],
    )
    frozen = contracts.freeze_contract_record(draft={**draft, "contract_payload_json": json.dumps(payload)}, audit={})
    rows = shared.contract_guardrail_rows(frozen, environment_name="dev", table_id="target-id")
    rules_frame = spark_session.createDataFrame(rows)
    frame = spark_session.createDataFrame([("treated",)], ["email"])
    result = shared.schema_check_core(frame, rules_df=rules_frame, table_id="target-id", environment_name="dev")
    assert result["status"] == "passed"
    assert result["can_continue"] is True


def test_later_write_failure_releases_token_mapping(monkeypatch, spark_session, write_workflow):
    """A publication failure cannot leak the mapping hidden by its raised exception."""
    _evidence, later = write_workflow
    rule = {"guardrail_rule_id": "sensitive-email", "guardrail_version": 1,
            "contract_id": "contract", "contract_version": 1,
            "guardrail_type": "sensitive_data", "column_id": "email-id", "column_name": "email",
            "rule_parameters_json": '{"scope":"column","treatment":"tokenize"}',
            "action": "Block", "is_active": True}
    monkeypatch.setattr(sensitive_module, "load_table_guardrail_rules", lambda *_args, **_kwargs: [rule])
    later["pipeline_write"].side_effect = ValueError("publication failed")
    frame = spark_session.createDataFrame([("raw@example.test",)], ["email"])
    before = spark_session.sparkContext._jsc.getPersistentRDDs().size()
    with pytest.raises(RuntimeError, match="publication failed"):
        run_pipeline_operation(orchestrate_write, frame, plan=execution_plan_stub(), sources=[], store="Silver", schema="dbo", table_name="customers",
                          write_mode="overwrite", spark_session=spark_session, verbose=False)
    assert spark_session.sparkContext._jsc.getPersistentRDDs().size() == before


@pytest.mark.parametrize('mode', ['testing', 'live'])
def test_simplified_mask_and_fixed_buckets_reach_the_public_write_workflow(monkeypatch, spark_session, write_workflow, mode):
    """DQ and publication receive the same protected rows declared by the contract."""
    evidence, later = write_workflow
    base = {'guardrail_version': 1, 'contract_id': 'contract', 'contract_version': 1,
            'guardrail_type': 'sensitive_data', 'action': 'Block', 'is_active': True}
    rules = [
        {**base, 'guardrail_rule_id': 'mask', 'column_id': 'email-id', 'column_name': 'email',
         'rule_parameters_json': json.dumps({'scope': 'column', 'treatment': 'mask',
                                            'preserve_start': 1, 'preserve_end': 1, 'mask_character': '*'})},
        {**base, 'guardrail_rule_id': 'bucket', 'column_id': 'age-id', 'column_name': 'age',
         'rule_parameters_json': json.dumps({'scope': 'column', 'treatment': 'bucket', 'bin_width': 10})},
    ]
    monkeypatch.setattr(sensitive_module, 'load_table_guardrail_rules', lambda *_args, **_kwargs: rules)
    frame = spark_session.createDataFrame([('ABC', 27), ('ALICE', 31)], ['email', 'age'])
    result = run_pipeline_operation(orchestrate_write, frame, sources=[], store='Silver', schema='dbo', table_name='customers',
        write_mode='overwrite', plan=execution_plan_stub(mode),
        spark_session=spark_session, verbose=False)
    assert [(r.email, r.age) for r in result['dataframe'].collect()] == [('***', '[20, 30)'), ('A***E', '[30, 40)')]
    assert later['check_dq'].call_args.args[0] is result['dataframe']
    assert result['published'] is (mode == 'live')
    assert len(evidence) == 2 and all(item['action'] == 'Block' for item in evidence)
    if mode == 'live':
        assert later['pipeline_write'].call_args.args[0] is result['dataframe']
    else:
        assert later['pipeline_write'].call_args.args[0] is result['dataframe']


@pytest.fixture(autouse=True)
def isolated_operation_journal(monkeypatch):
    """Stage unit tests isolate run storage; lifecycle tests exercise the real journal."""
    from contextlib import nullcontext
    from importlib import import_module
    from unittest.mock import Mock

    for name in ("orchestrate_read", "orchestrate_write"):
        monkeypatch.setattr(import_module(f"fabricops_kit.pipeline.{name}"), "PipelineOperation",
                            lambda _plan, _role, arguments: nullcontext(Mock(arguments=arguments)))
