"""Shared-plan integration and durable-boundary spies for Testing and Live."""

import importlib
import json
from dataclasses import FrozenInstanceError
from unittest.mock import Mock

import pytest

from fabricops_kit import setup_pipeline, orchestrate_read, orchestrate_write
from fabricops_kit.pipeline import shared
from tests.helpers import framework_config
from tests.unit.test_data_contract_resolution import RecordingFrame

plan_module = importlib.import_module("fabricops_kit.pipeline.shared")
read_module = importlib.import_module("fabricops_kit.pipeline.pipeline_read")
write_module = importlib.import_module("fabricops_kit.pipeline.pipeline_write")
profile_module = importlib.import_module("fabricops_kit.pipeline.profile_table")

SOURCE = {"store": "Bronze", "schema": "demo", "table_name": "source"}
TARGET = {"store": "Silver", "schema": "demo", "table_name": "target"}
SOURCE_ID = shared.resolve_physical_table_identity(framework_config(), "dev", **SOURCE)["table_id"]
TARGET_ID = shared.resolve_physical_table_identity(framework_config(), "dev", **TARGET)["table_id"]


def frozen(table_id, *, version=1, active=False, strategy="overwrite", parameters=None):
    """Build a valid canonical frozen payload with Schema and a precise DQ rule."""
    contract_id = "contract-" + table_id
    payload = {
        "contract": {"contract_id": contract_id, "contract_version": version},
        "table": {"table_id": table_id, "columns": [{"column_id": "id-col", "column_name": "id", "data_type": "bigint"}],
                  "processing": {"load_strategy": strategy, **(parameters or {})},
                  "writer": {"notebook_name": "Pipeline", "notebook_id": "notebook"}},
        "enrichment": {"table": [], "columns": []},
        "guardrails": [
            {"guardrail_rule_id": table_id + "-schema", "guardrail_version": 1,
             "guardrail_type": "schema", "rule_type": "required_columns", "rule_parameters": {"required_columns": ["id-col"]},
             "action": "Block", "is_active": True},
            {"guardrail_rule_id": table_id + "-dq", "guardrail_version": 1,
             "guardrail_type": "data_quality", "rule_type": "completeness", "column_id": "id-col",
             "rule_parameters": {"columns": ["id"], "maximum_missing_percent": 0, "treat_blank_as_missing": False},
             "action": "Block", "is_active": True},
        ],
    }
    return {"table_id": table_id, "contract_id": contract_id, "contract_version": version,
            "environment_name": "dev", "status": "frozen", "is_active": active,
            "agreement_id": "agreement", "agreement_version": "1", "contract_payload_json": json.dumps(payload)}


@pytest.fixture
def runtime(monkeypatch, spark_session):
    """Real Spark evaluations and orchestrators; replace only Fabric boundaries."""
    config = framework_config()
    context = {"config": config, "env": "dev", "notebook_id": "notebook", "notebook_name": "Pipeline",
               "workspace_id": "workspace", "workspace_name": "Workspace", "user_name": "tester", "activity_id": "activity"}
    rows = []
    source = spark_session.createDataFrame([(1,), (2,)], "id long")
    monkeypatch.setattr(plan_module, "resolve_fabric_context", lambda context=None: (config, "dev", context or runtime_context))
    runtime_context = context
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: (config, "dev", context or runtime_context))
    monkeypatch.setattr(shared, "get_spark_session", lambda *a: spark_session)
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda name, **kw: RecordingFrame(rows) if name == "METADATA_DATA_CONTRACT" else (_ for _ in ()).throw(RuntimeError("[TABLE_OR_VIEW_NOT_FOUND] Table does not exist")))
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: source)
    monkeypatch.setattr(write_module, "_target_has_activity", lambda **kw: False)
    monkeypatch.setattr(write_module, "_target_has_rows", lambda **kw: False)
    # Every mutation reachable from Read, validation, recovery and Write is observed.
    spies = {}
    for owner, names in ((shared, ["write_lakehouse_table", "persist_lineage_participation"]),
                         (profile_module, ["_replace_snapshot_rows", "_replace_frequency_rows", "_upsert_catalogue_identities", "_delete_profile_snapshot", "_stage_catalogue_profile_retry"]),
                         (write_module, ["_persist_target_processing"]),
                         (importlib.import_module("fabricops_kit.io"), ["write_lakehouse_table", "write_warehouse_table"]),
                         (importlib.import_module("fabricops_kit.io.shared"), ["execute_warehouse_processing"])):
        for name in names:
            spy = Mock(name=name)
            monkeypatch.setattr(owner, name, spy)
            spies[f"{owner.__name__}.{name}"] = spy
    def make(mode="testing", contracted=False, strategy="overwrite", parameters=None):
        if contracted and not rows:
            rows.extend([frozen(SOURCE_ID, active=mode == "live"), frozen(TARGET_ID, active=mode == "live", strategy=strategy, parameters=parameters)])
        selections = {row["table_id"]: {"contract_id": row["contract_id"], "contract_version": row["contract_version"]} for row in rows}
        if not contracted:
            selections = {SOURCE_ID: {"no_contract": True}, TARGET_ID: {"no_contract": True}}
        return setup_pipeline(interactive=False, execution_mode=mode, sources=[SOURCE], targets=[TARGET],
                                              selections=selections, context=context, spark_session=spark_session)
    return make, rows, spies, context


def read(plan, spark, **kwargs):
    """Use real Read with expensive optional profiling work disabled."""
    return orchestrate_read(execution_plan=plan, **SOURCE, spark_session=spark, verbose=False,
                            grain_discovery_enabled=False, frequency_enabled=False, **kwargs)


def write(plan, source, spark, dataframe=None, strategy="overwrite", parameters=None):
    """Use the real target lifecycle."""
    return orchestrate_write(source["dataframe"] if dataframe is None else dataframe, execution_plan=plan,
                             sources=[source], **TARGET, write_mode=strategy, write_parameters=parameters,
                             grain_discovery_enabled=False, frequency_enabled=False, verbose=False, spark_session=spark)


@pytest.mark.parametrize("strategy,parameters", [("overwrite", None), ("append", None),
    ("scd1", {"key_columns": ["id"]}), ("scd2", {"key_columns": ["id"], "effective_column": "id"})])
def test_testing_all_strategies_have_zero_durable_mutations(runtime, spark_session, strategy, parameters):
    """Read/profile/check/write paths evaluate but no durable boundary is called."""
    make, _, spies, _ = runtime
    plan = make(strategy=strategy, parameters=parameters)
    source = read(plan, spark_session)
    result = write(plan, source, spark_session, strategy=strategy, parameters=parameters)
    assert source["execution_mode"] == result["execution_mode"] == "testing"
    assert not result["published"] and result["write_metrics"]["rows_committed"] == 0
    assert result["dry_run"]["status"] == "passed" and result["checks_not_exercised"]
    assert ("SCD business keys" in result["dry_run"]["fully_evaluated"]) is (strategy in {"scd1", "scd2"})
    assert all(spy.call_count == 0 for spy in spies.values())


def test_testing_real_guardrails_return_results_without_activation_evidence(runtime, spark_session):
    """Read and Write retain exact rule results without metadata writes."""
    make, _, spies, _ = runtime
    plan = make(contracted=True)
    source = read(plan, spark_session)
    result = write(plan, source, spark_session)
    assert "coverage_result" not in result
    assert len(result["source_guardrail_results"]) == 2
    assert len(plan.results) == 4
    assert all(row["rule_type"] != "contract_validation" for row in plan.results)
    assert result["validation_passed"] and not result["published"]
    assert all(spy.call_count == 0 for spy in spies.values())


def test_testing_failed_guardrail_returns_violations_without_publication(runtime, spark_session):
    """A failed target DQ rule remains inspectable and cannot count as a passed dry run."""
    make, _, spies, _ = runtime
    plan = make(contracted=True)
    source = read(plan, spark_session)
    bad = spark_session.createDataFrame([(None,)], "id long")
    result = write(plan, source, spark_session, dataframe=bad)
    assert result["dq_result"]["can_continue"] is False
    assert result["validation_passed"] is False
    assert not result["published"]
    assert all(spy.call_count == 0 for spy in spies.values())


def test_live_guardrail_blocking_prevents_physical_publication(runtime, spark_session):
    """Live preserves Block decisions before entering any business writer."""
    make, _, spies, _ = runtime
    plan = make("live", contracted=True)
    source = read(plan, spark_session)
    bad = spark_session.createDataFrame([(None,)], "id long")
    with pytest.raises(RuntimeError, match="Data Quality"):
        write(plan, source, spark_session, dataframe=bad)
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 0
    assert spies["fabricops_kit.pipeline.shared.write_lakehouse_table"].call_count > 0


def test_immutable_plan_and_cross_run_sources_are_rejected(runtime, spark_session):
    """No mutable widget state or source from a different mode can authorize a write."""
    make, _, _, _ = runtime
    testing = make()
    with pytest.raises(FrozenInstanceError):
        testing.execution_mode = "live"
    source = read(testing, spark_session)
    live = make("live")
    with pytest.raises(ValueError, match="same execution plan"):
        write(live, source, spark_session)


def test_headless_requires_mode_and_every_explicit_choice(runtime):
    """Headless callers cannot infer Live or silently omit table choices."""
    _, _, _, context = runtime
    with pytest.raises(ValueError, match="execution_mode"):
        setup_pipeline(interactive=False, sources=[SOURCE], targets=[TARGET], selections={}, context=context)
    with pytest.raises(ValueError, match="every participating"):
        setup_pipeline(interactive=False, execution_mode="testing", sources=[SOURCE], targets=[TARGET], selections={}, context=context)


@pytest.mark.parametrize("strategy,parameters", [("append", None), ("scd1", {"key_columns": ["id"]}),
    ("scd2", {"key_columns": ["id"], "effective_column": "id"})])
def test_testing_incremental_bootstrap_does_not_advance_checkpoints(runtime, spark_session, strategy, parameters):
    """Incremental reads evaluate real bounds and all supported incremental strategies without writes."""
    make, _, spies, _ = runtime
    plan = make()
    source = read(plan, spark_session, read_mode="incremental", read_parameters={"watermark_column": "id"}, target_table_id=TARGET_ID)
    result = write(plan, source, spark_session, strategy=strategy, parameters=parameters)
    assert source["scope"]["first_run"]
    assert source["dataframe"].count() == 2
    assert not result["published"] and result["validation_passed"]
    assert all(spy.call_count == 0 for spy in spies.values())


def test_testing_observation_recovery_cannot_merge_durable_state(runtime, monkeypatch):
    """The common native Delta merge boundary obeys the run policy before any IO."""
    make, _, _, context = runtime
    plan = make()
    create_spark = Mock(side_effect=AssertionError("must not reach physical merge"))
    monkeypatch.setattr(shared, "get_spark_session", create_spark)
    shared._merge_source_observation_records([{"observation_status": "committed"}],
        config=context["config"], context={**context, "execution_plan": plan})
    create_spark.assert_not_called()


def test_live_explicit_bootstrap_publishes_and_commits_lineage(runtime, spark_session, monkeypatch):
    """An explicit uncontracted Live bootstrap works without historical Lineage."""
    make, _, spies, _ = runtime
    plan = make("live")
    monkeypatch.setattr(write_module, "_writer_scheduled_refresh", lambda **kw: {"status": "not_configured", "schedules": []})
    orchestrator = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    monkeypatch.setattr(orchestrator, "profile_table", lambda **kw: {"row_count": 2})
    source = read(plan, spark_session)
    result = write(plan, source, spark_session)
    assert result["published"] and result["execution_mode"] == "live"
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 1
    assert spies["fabricops_kit.pipeline.shared.persist_lineage_participation"].call_count == 2
    assert spies["fabricops_kit.pipeline.pipeline_write._persist_target_processing"].call_count == 1


@pytest.mark.parametrize("mode", ["testing", "live"])
@pytest.mark.parametrize("contracted_id", [SOURCE_ID, TARGET_ID])
def test_mixed_relationship_respects_explicit_no_contract(runtime, spark_session, monkeypatch, mode, contracted_id):
    """Explicit opt-out exempts one participant, retaining the selected contract's checks."""
    _, rows, spies, context = runtime
    candidate = frozen(contracted_id, active=mode == "live")
    rows.append(candidate)
    selections = {SOURCE_ID: {"no_contract": True}, TARGET_ID: {"no_contract": True}}
    selections[contracted_id] = {"contract_id": candidate["contract_id"], "contract_version": 1}
    plan = setup_pipeline(interactive=False, execution_mode=mode, sources=[SOURCE], targets=[TARGET],
        selections=selections, context=context, spark_session=spark_session)
    monkeypatch.setattr(write_module, "_writer_scheduled_refresh", lambda **kw: {"status": "not_configured", "schedules": []})
    orchestrator = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    if mode == "live":
        monkeypatch.setattr(orchestrator, "profile_table", lambda **kw: {"row_count": 2})
    result = write(plan, read(plan, spark_session), spark_session)
    assert len(plan.results) == 2
    assert all(item["can_continue"] for item in result["source_guardrail_results"])
    assert result["published"] is (mode == "live")
    if mode == "testing":
        assert result["validation_passed"]
        assert all(spy.call_count == 0 for spy in spies.values())
    else:
        assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 1
        assert spies["fabricops_kit.pipeline.shared.persist_lineage_participation"].call_count == 2


@pytest.mark.parametrize("strategy,parameters", [("scd1", {"key_columns": ["id"]}),
    ("scd2", {"key_columns": ["id"], "effective_column": "missing"})])
def test_testing_processing_failure_returns_prepared_diagnostics_without_mutation(runtime, spark_session, strategy, parameters):
    """Invalid proposed SCD input is a failed dry run with inspectable rows and no writes."""
    make, _, spies, _ = runtime
    plan = make()
    source = read(plan, spark_session)
    invalid = spark_session.createDataFrame([(1,), (1,)], "id long")
    result = write(plan, source, spark_session, dataframe=invalid, strategy=strategy, parameters=parameters)
    assert not result["validation_passed"] and result["dry_run"]["status"] == "blocked"
    assert result["dataframe"] is invalid
    assert result["dry_run"]["reason"] and not result["published"]
    assert all(spy.call_count == 0 for spy in spies.values())


def test_testing_missing_dq_column_reports_unevaluated_check_without_losing_rows(runtime, spark_session):
    """Schema drift can make DQ unexercisable; Testing reports that distinction explicitly."""
    make, _, spies, _ = runtime
    plan = make(contracted=True)
    source = read(plan, spark_session)
    changed = source["dataframe"].selectExpr("id as unexpected")
    result = write(plan, source, spark_session, dataframe=changed)
    assert result["dataframe"] is changed and not result["validation_passed"]
    assert result["dq_result"]["evaluation_status"] == "not_fully_evaluated"
    assert any("Data Quality:" in check for check in result["checks_not_exercised"])
    assert not result["published"] and all(spy.call_count == 0 for spy in spies.values())


def test_failed_read_cannot_reuse_prior_successful_dq_evidence(runtime, spark_session, monkeypatch):
    """A missing optional Schema column invalidates its previous passing DQ check."""
    make, rows, spies, _ = runtime
    make(contracted=True)
    payload = json.loads(rows[0]["contract_payload_json"])
    payload["table"]["columns"].append({"column_id": "other-col", "column_name": "other", "data_type": "bigint"})
    payload["guardrails"][1]["column_id"] = "other-col"
    payload["guardrails"][1]["rule_parameters"]["columns"] = ["other"]
    rows[0]["contract_payload_json"] = json.dumps(payload)
    plan = make(contracted=True)
    initial = spark_session.createDataFrame([(1, 1), (2, 2)], "id long, other long")
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: initial)
    read(plan, spark_session)
    changed = initial.drop("other")
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: changed)
    failed = read(plan, spark_session)
    assert failed["dq_result"]["can_continue"] is False
    result = write(plan, failed, spark_session)
    assert not result["validation_passed"]
    from fabricops_kit.widgets.widget_activate_data_contract import _diagnostic_review
    assert not _diagnostic_review([result], rows[0], "dev")["available"]
    # Reevaluation can recover without creating a new plan or retaining stale failures.
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: initial)
    recovered = read(plan, spark_session)
    assert write(plan, recovered, spark_session, dataframe=recovered["dataframe"].select("id"))["validation_passed"]
    # A later passing Read cannot turn the earlier failed Read result into a passing report.
    assert not write(plan, failed, spark_session)["validation_passed"]
    assert all(spy.call_count == 0 for spy in spies.values())


@pytest.mark.parametrize("mode", ["testing", "live"])
def test_no_contract_target_does_not_exempt_failed_source_checks(runtime, spark_session, monkeypatch, mode):
    """An explicit target opt-out cannot waive Block outcomes on its contracted source."""
    _, rows, spies, context = runtime
    candidate = frozen(SOURCE_ID, active=mode == "live")
    rows.append(candidate)
    plan = setup_pipeline(interactive=False, execution_mode=mode, sources=[SOURCE], targets=[TARGET],
        selections={SOURCE_ID: {"contract_id": candidate["contract_id"], "contract_version": 1},
                    TARGET_ID: {"no_contract": True}}, context=context, spark_session=spark_session)
    bad = spark_session.createDataFrame([(None,)], "id long")
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: bad)
    if mode == "live":
        with pytest.raises(RuntimeError, match="Data Quality"):
            read(plan, spark_session)
    else:
        source = read(plan, spark_session)
        result = write(plan, source, spark_session)
        assert not result["validation_passed"]
        assert all(spy.call_count == 0 for spy in spies.values())
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 0


@pytest.mark.parametrize("mode", ["testing", "live"])
@pytest.mark.parametrize("disabled", [False, True])
def test_empty_or_disabled_contract_checks_do_not_require_minimum_coverage(runtime, spark_session, monkeypatch, mode, disabled):
    """An authored empty or disabled set imposes no extra publication decision."""
    make, rows, spies, _ = runtime
    make(mode, contracted=True)
    originals = []
    for row in rows:
        payload = json.loads(row["contract_payload_json"])
        payload["guardrails"] = [{**rule, "is_active": False} for rule in payload["guardrails"]] if disabled else []
        row["contract_payload_json"] = json.dumps(payload)
        originals.append(row["contract_payload_json"])
    plan = make(mode, contracted=True)
    monkeypatch.setattr(write_module, "_writer_scheduled_refresh", lambda **kw: {"status": "not_configured", "schedules": []})
    orchestrator = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    if mode == "live":
        monkeypatch.setattr(orchestrator, "profile_table", lambda **kw: {"row_count": 2})
    result = write(plan, read(plan, spark_session), spark_session)
    assert result["published"] is (mode == "live")
    assert result["source_guardrail_results"] == [] and plan.results == []
    assert "coverage_result" not in result
    assert not any("Coverage" in stage["stage"] for stage in result["orchestration_stages"])
    assert [row["contract_payload_json"] for row in rows] == originals
    if mode == "testing":
        assert result["validation_passed"]
        assert all(spy.call_count == 0 for spy in spies.values())


@pytest.mark.parametrize("mode", ["testing", "live"])
def test_required_guardrail_that_skips_cannot_authorize_publication(runtime, spark_session, monkeypatch, mode):
    """A configured check that cannot execute fails closed even without a gate."""
    make, _, spies, _ = runtime
    plan = make(mode, contracted=True)
    source = read(plan, spark_session)
    orchestrator = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    monkeypatch.setattr(orchestrator, "check_dq", lambda *a, **kw: {"status": "skipped", "can_continue": True})
    if mode == "live":
        with pytest.raises(RuntimeError, match="configured Guardrail did not execute"):
            write(plan, source, spark_session)
    else:
        result = write(plan, source, spark_session)
        assert not result["validation_passed"] and not result["published"]
        assert result["dq_result"]["evaluation_status"] == "not_fully_evaluated"
        assert all(spy.call_count == 0 for spy in spies.values())
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 0


@pytest.mark.parametrize("mode", ["testing", "live"])
def test_warn_failures_report_and_permit_configured_write(runtime, spark_session, monkeypatch, mode):
    """Warn retains violations and allows Live publication after configured checks."""
    make, rows, spies, _ = runtime
    make(mode, contracted=True)
    for row in rows:
        payload = json.loads(row["contract_payload_json"])
        payload["guardrails"][1]["action"] = "Warn"
        row["contract_payload_json"] = json.dumps(payload)
    plan = make(mode, contracted=True)
    monkeypatch.setattr(write_module, "_writer_scheduled_refresh", lambda **kw: {"status": "not_configured", "schedules": []})
    orchestrator = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    if mode == "live":
        monkeypatch.setattr(orchestrator, "profile_table", lambda **kw: {"row_count": 1})
    source = read(plan, spark_session)
    result = write(plan, source, spark_session, dataframe=spark_session.createDataFrame([(None,)], "id long"))
    assert result["dq_result"]["status"] == "warning"
    assert result["dq_result"]["can_continue"]
    assert result["published"] is (mode == "live")
    if mode == "testing":
        assert result["validation_passed"]
        assert all(spy.call_count == 0 for spy in spies.values())


@pytest.mark.parametrize("key", ["coverage_gate", "coverage_policy", "coverage_gate_policy", "guardrail_coverage"])
@pytest.mark.parametrize("location", ["contract", "table", "guardrail"])
def test_legacy_coverage_settings_require_explicit_new_contract_migration(key, location):
    """Never silently discard a legacy requirement or mutate its frozen payload."""
    from fabricops_kit.data_contract.shared import validate_contract_definitions
    record = frozen(TARGET_ID)
    payload = json.loads(record["contract_payload_json"])
    validate_contract_definitions(payload)
    definition = {"contract": payload, "table": payload["table"], "guardrail": payload["guardrails"][0]}[location]
    definition[key] = {"action": "Block", "required": ["schema"]}
    original = json.dumps(payload, sort_keys=True)
    with pytest.raises(ValueError, match="requires migration"):
        validate_contract_definitions(payload)
    assert json.dumps(payload, sort_keys=True) == original


@pytest.mark.parametrize("field,value", [("contract_version", 99), ("contract_id", "other"),
    ("guardrail_version", 99), ("table_id", "other"), ("guardrail_type", "grain")])
def test_live_rejects_source_results_for_another_contract_or_rule(runtime, spark_session, field, value):
    """Configured source rules require exact identities rather than any passing result."""
    make, _, spies, _ = runtime
    plan = make("live", contracted=True)
    source = read(plan, spark_session)
    for result in source["guardrail_outcomes"]:
        result[field] = value
    with pytest.raises(RuntimeError, match="configured .* Guardrail has no successful Read result"):
        write(plan, source, spark_session)
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 0


def test_caught_live_read_failure_cannot_publish_using_an_earlier_success(runtime, spark_session, monkeypatch):
    """Required Read execution survives removal of the independent coverage stage."""
    make, _, spies, _ = runtime
    plan = make("live", contracted=True)
    earlier_source = read(plan, spark_session)
    bad = spark_session.createDataFrame([(None,)], "id long")
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: bad)
    with pytest.raises(RuntimeError, match="Data Quality"):
        read(plan, spark_session)
    with pytest.raises(RuntimeError, match="configured data_quality Guardrail has no successful Read result"):
        write(plan, earlier_source, spark_session)
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 0


def test_legacy_coverage_guardrail_is_rejected_without_rewriting_other_policies():
    """Unsupported authored enforcement must be reviewed in a new contract version."""
    from fabricops_kit.data_contract.shared import validate_contract_definitions
    payload = json.loads(frozen(TARGET_ID)["contract_payload_json"])
    payload["guardrails"].append({"guardrail_type": "guardrail_coverage", "action": "Block", "is_active": True,
                                  "guardrail_rule_id": "old-coverage", "rule_parameters": {}})
    original = json.dumps(payload, sort_keys=True)
    with pytest.raises(ValueError, match="unsupported Guardrail definition"):
        validate_contract_definitions(payload)
    assert json.dumps(payload, sort_keys=True) == original


@pytest.mark.parametrize("column_name", ["coverage_gate", "coverage_policy", "coverage_gate_policy", "guardrail_coverage"])
def test_legacy_setting_names_are_valid_column_names_in_schema_mappings(column_name):
    """Data keys must not be interpreted as obsolete execution configuration."""
    from fabricops_kit.data_contract.shared import validate_contract_definitions
    payload = json.loads(frozen(TARGET_ID)["contract_payload_json"])
    payload["table"]["columns"][0]["column_name"] = column_name
    payload["guardrails"] = payload["guardrails"][:1]
    payload["guardrails"][0]["rule_parameters"]["data_types"] = {column_name: "bigint"}
    original = json.dumps(payload, sort_keys=True)
    validate_contract_definitions(payload)
    rows = shared.contract_guardrail_rows({"contract_payload": payload}, environment_name="dev", table_id=TARGET_ID)
    assert json.loads(rows[0]["rule_parameters_json"])["data_types"] == {column_name: "bigint"}
    assert json.dumps(payload, sort_keys=True) == original
