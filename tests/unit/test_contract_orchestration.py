"""Shared-plan integration and durable-boundary spies for Testing and Live."""

from contextlib import nullcontext
from types import SimpleNamespace
import importlib
import hashlib
import json
from dataclasses import FrozenInstanceError
from unittest.mock import Mock

import pytest

from fabricops_kit.pipeline.shared import build_pipeline_execution_plan as setup_pipeline
from fabricops_kit import orchestrate_read, orchestrate_write
from fabricops_kit.pipeline import shared
from tests.helpers import framework_config
from tests.unit.test_data_contract_resolution import RecordingFrame
from tests.helpers import run_pipeline_operation

plan_module = importlib.import_module("fabricops_kit.pipeline.shared")
read_module = importlib.import_module("fabricops_kit.pipeline.pipeline_read")
write_module = importlib.import_module("fabricops_kit.pipeline.pipeline_write")
profile_module = importlib.import_module("fabricops_kit.pipeline.shared")

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
            "workspace_id": "dev", "status": "frozen", "is_active": active,
            "agreement_id": "agreement", "agreement_version": "1", "contract_payload_json": json.dumps(payload)}


@pytest.fixture
def runtime(monkeypatch, spark_session):
    """Real Spark evaluations and orchestrators; replace only Fabric boundaries."""
    from importlib import metadata
    installed_version = metadata.version
    monkeypatch.setattr(metadata, "version", lambda name: "test-delta-runtime" if name == "delta-spark" else installed_version(name))
    import sys

    class Merge:
        def alias(self, name): return self
        def merge(self, frame, condition):
            self.row = frame.collect()[0].asDict(recursive=True)
            return self
        def toDF(self):
            from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
            return spark_session.createDataFrame([], metadata_table_schema_registry()["METADATA_PROCESSING_STATE"])
        def whenMatchedUpdate(self, **kwargs): return self
        def whenMatchedUpdateAll(self): return self
        def whenNotMatchedInsertAll(self): return self
        def execute(self): run_rows.append(self.row)

    run_rows = []
    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=SimpleNamespace(forPath=lambda *a: Merge())))
    config = framework_config()
    context = {"config": config, "scope_workspace_id": "dev", "notebook_id": "notebook", "notebook_name": "Pipeline",
               "workspace_id": "workspace", "workspace_name": "Workspace", "user_name": "tester", "activity_id": "activity"}
    rows = []
    source = spark_session.createDataFrame([(1,), (2,)], "id long")
    monkeypatch.setattr(plan_module, "resolve_fabric_context", lambda context=None: (config, "dev", context or runtime_context))
    runtime_context = context
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: (config, "dev", context or runtime_context))
    monkeypatch.setattr(shared, "get_spark_session", lambda *a, **_kwargs: spark_session)
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda name, **kw: RecordingFrame(rows) if name == "METADATA_DATA_CONTRACT" else RecordingFrame([]) if name == "METADATA_ACTIVATED_PIPELINE" else (_ for _ in ()).throw(RuntimeError("[TABLE_OR_VIEW_NOT_FOUND] Table does not exist")))
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: source)
    monkeypatch.setattr(shared, "PublicationBatch", lambda dataframe, **kw: nullcontext(SimpleNamespace(
        dataframe=dataframe, audit=kw["audit"], receipt={"batch_id": "batch", "activity_id": kw["audit"]["_activity_id"],
                                                       "committed_at": "2026-09-11T02:00:00+00:00", "input_rows": 2,
                                                       "strategy": kw["processing"]["load_strategy"], "run_id": shared.source_observation_run_id(kw["context"])}, input_rows=2, already_applied=False, finalization_recovery=False, publication_snapshot=[], confirm=lambda: None,
    )))
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
    # These tests isolate runtime Guardrail/publication boundaries. Full approval,
    # deployment and journal authorization are exercised in test_activated_pipeline
    # and the authored lifecycle integration test, rather than legacy active flags.
    from dataclasses import replace
    from fabricops_kit.activated_pipeline import shared as activation
    monkeypatch.setattr(activation, "verify_live_plan", lambda *a, **kw: None)
    journal = shared.PipelineOperation
    def verified_journal(plan, role, arguments):
        if plan.execution_mode == "live" and plan.evidence["failures"]:
            raise RuntimeError("Pipeline run previously failed; create a new plan.")
        return journal(replace(plan, execution_mode="testing") if plan.execution_mode == "live" else plan, role, arguments)
    for name in ("orchestrate_read", "orchestrate_write"):
        monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline." + name), "PipelineOperation", verified_journal)
    def make(mode="testing", contracted=False, strategy="overwrite", parameters=None):
        if contracted and not rows:
            rows.extend([frozen(SOURCE_ID, active=mode == "live"), frozen(TARGET_ID, active=mode == "live", strategy=strategy, parameters=parameters)])
        selections = {row["table_id"]: {"contract_id": row["contract_id"], "contract_version": row["contract_version"]} for row in rows}
        if not contracted:
            selections = {SOURCE_ID: {"no_contract": True}, TARGET_ID: {"no_contract": True}}
        plan = setup_pipeline(execution_mode="testing" if mode == "live" else mode, sources=[SOURCE], targets=[TARGET],
                                              selections=selections, context=context, spark_session=spark_session, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52")
        return replace(plan, execution_mode="live", approval_id="verified-by-boundary") if mode == "live" else plan
    for name in ("orchestrate_read", "orchestrate_write"):
        monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline." + name), "schedule_table_profiling",
                            lambda *args, **kwargs: {"status": "passed", "row_count": 2})
    return make, rows, spies, context


def read(plan, spark, **kwargs):
    """Use real Read with expensive optional profiling work disabled."""
    return run_pipeline_operation(orchestrate_read, plan=plan, **SOURCE, spark_session=spark, verbose=False,
                              **kwargs)


def write(plan, source, spark, dataframe=None, strategy="overwrite", parameters=None):
    """Use the real target lifecycle."""
    return run_pipeline_operation(orchestrate_write, source["dataframe"] if dataframe is None else dataframe, plan=plan,
                             sources=[source], **TARGET, write_mode=strategy, write_parameters=parameters,
                               verbose=False, spark_session=spark)


@pytest.mark.parametrize("strategy,parameters", [("overwrite", None), ("append", None),
    ("scd1", {"key_columns": ["id"]}), ("scd2", {"key_columns": ["id"], "effective_column": "id"})])
def test_testing_all_strategies_have_only_diagnostic_mutations(runtime, spark_session, strategy, parameters):
    """Read/profile/check/write paths evaluate but no durable boundary is called."""
    make, _, spies, _ = runtime
    plan = make(strategy=strategy, parameters=parameters)
    source = read(plan, spark_session)
    result = write(plan, source, spark_session, strategy=strategy, parameters=parameters)
    assert source["execution_mode"] == result["execution_mode"] == "testing"
    assert not result["published"] and result["write_metrics"]["rows_committed"] == 0
    assert result["dry_run"]["status"] == "passed" and result["checks_not_exercised"]
    assert ("SCD business keys" in result["dry_run"]["fully_evaluated"]) is (strategy in {"scd1", "scd2"})
    assert_testing_mutations_are_diagnostics_only(spies)


def test_testing_real_guardrails_persist_linked_diagnostics(runtime, spark_session):
    """Read and Write persist exact rule results linked to the complete logical run."""
    make, _, spies, _ = runtime
    plan = make(contracted=True)
    source = read(plan, spark_session)
    result = write(plan, source, spark_session)
    assert "coverage_result" not in result
    assert len(result["source_guardrail_results"]) == 2
    assert len(plan.results) == 4
    assert all(row["run_id"] == plan.plan_id for row in plan.results)
    from fabricops_kit.pipeline.shared import finalize_pipeline_run
    finalized = finalize_pipeline_run(plan, spark_session=spark_session)
    assert finalized["status"] == "incomplete"
    assert all(row["rule_type"] != "contract_validation" for row in plan.results)
    assert result["validation_passed"] and not result["published"]
    assert_testing_mutations_are_diagnostics_only(spies)


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
    assert_testing_mutations_are_diagnostics_only(spies)


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
    other = make()
    with pytest.raises(ValueError, match="same execution plan"):
        write(other, source, spark_session)


def test_headless_requires_mode_and_every_explicit_choice(runtime):
    """Headless callers cannot infer Live or silently omit table choices."""
    _, _, _, context = runtime
    with pytest.raises(ValueError, match="every participating"):
        setup_pipeline(execution_mode="testing", sources=[SOURCE], targets=[TARGET], selections={}, context=context, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52")
    with pytest.raises(ValueError, match="every participating"):
        setup_pipeline(execution_mode="testing", sources=[SOURCE], targets=[TARGET], selections={}, context=context, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52")


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
    assert_testing_mutations_are_diagnostics_only(spies)


def test_testing_observation_recovery_cannot_merge_durable_state(runtime, monkeypatch):
    """The common native Delta merge boundary obeys the run policy before any IO."""
    make, _, _, context = runtime
    plan = make()
    create_spark = Mock(side_effect=AssertionError("must not reach physical merge"))
    monkeypatch.setattr(shared, "get_spark_session", create_spark)
    shared._merge_source_observation_records([{"observation_status": "committed"}],
        config=context["config"], context={**context, "execution_plan": plan})
    create_spark.assert_not_called()


@pytest.mark.parametrize("mode", ["live"])
@pytest.mark.parametrize("schedule_available", [True, False])
def test_initial_publication_publishes_and_commits_lineage(runtime, spark_session, monkeypatch, mode, schedule_available):
    """Initial publication uses its explicit policy without requiring historical Lineage."""
    make, _, spies, _ = runtime
    plan = make(mode, contracted=mode == "live")
    schedule = importlib.import_module("fabricops_kit.data_contract.scheduled_refresh")

    def discover(**kwargs):
        if not schedule_available:
            raise PermissionError("Schedule access unavailable")
        return {"status": "not_configured", "schedules": []}

    monkeypatch.setattr(schedule, "discover_scheduled_refresh", discover)
    orchestrator = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    monkeypatch.setattr(orchestrator, "schedule_table_profiling", lambda *args, **kw: {"row_count": 2})
    source = read(plan, spark_session)
    result = write(plan, source, spark_session)
    assert result["published"] and result["execution_mode"] == mode
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 1
    assert spies["fabricops_kit.pipeline.shared.persist_lineage_participation"].call_count == 2
    assert spies["fabricops_kit.pipeline.pipeline_write._persist_target_processing"].call_count == 1
    capture = spies["fabricops_kit.pipeline.pipeline_write._persist_target_processing"].call_args.kwargs["scheduled_refresh"]
    assert capture == {"status": "not_configured" if schedule_available else "unavailable", "schedules": []}


@pytest.mark.parametrize("mode", ["testing", "live"])
@pytest.mark.parametrize("contracted_id", [SOURCE_ID, TARGET_ID])
def test_mixed_relationship_respects_explicit_no_contract(runtime, spark_session, monkeypatch, mode, contracted_id):
    """Explicit opt-out exempts one participant, retaining the selected contract's checks."""
    _, rows, spies, context = runtime
    candidate = frozen(contracted_id, active=mode == "live")
    rows.append(candidate)
    selections = {SOURCE_ID: {"no_contract": True}, TARGET_ID: {"no_contract": True}}
    selections[contracted_id] = {"contract_id": candidate["contract_id"], "contract_version": 1}
    if mode == "live":
        with pytest.raises(ValueError, match="Governed"):
            setup_pipeline(execution_mode=mode, sources=[SOURCE], targets=[TARGET],
                selections=selections, context=context, spark_session=spark_session, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52")
        assert_testing_mutations_are_diagnostics_only(spies)
        return
    plan = setup_pipeline(execution_mode=mode, sources=[SOURCE], targets=[TARGET],
                          selections=selections, context=context, spark_session=spark_session, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52")
    source = read(plan, spark_session)
    result = write(plan, source, spark_session)
    assert result["validation_passed"] and not result["published"]
    assert {row["table_id"] for row in plan.results} == {contracted_id}
    assert len(plan.results) == 2
    assert_testing_mutations_are_diagnostics_only(spies)



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
    assert_testing_mutations_are_diagnostics_only(spies)


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
    assert not result["published"]
    assert_testing_mutations_are_diagnostics_only(spies)


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
    with pytest.raises(ValueError, match="Duplicate operation"):
        read(plan, spark_session)
    from fabricops_kit.pipeline.shared import finalize_pipeline_run
    assert finalize_pipeline_run(plan, spark_session=spark_session)["status"] == "failed"
    plan = make(contracted=True)
    failed = read(plan, spark_session)
    assert failed["dq_result"]["can_continue"] is False
    result = write(plan, failed, spark_session)
    assert not result["validation_passed"]
    assert result["validation_passed"] is False
    # Reevaluation uses a new plan, preserving the failed run for inspection.
    assert finalize_pipeline_run(plan, spark_session=spark_session)["status"] == "failed"
    plan = make(contracted=True)
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: initial)
    recovered = read(plan, spark_session)
    assert write(plan, recovered, spark_session, dataframe=recovered["dataframe"].select("id"))["validation_passed"]
    # A later passing Read cannot turn the earlier failed Read result into a passing report.
    assert result["validation_passed"] is False
    assert_testing_mutations_are_diagnostics_only(spies)


@pytest.mark.parametrize("mode", ["testing", "live"])
def test_no_contract_target_does_not_exempt_failed_source_checks(runtime, spark_session, monkeypatch, mode):
    """An explicit target opt-out cannot waive Block outcomes on its contracted source."""
    _, rows, spies, context = runtime
    candidate = frozen(SOURCE_ID, active=mode == "live")
    rows.append(candidate)
    selections = {SOURCE_ID: {"contract_id": candidate["contract_id"], "contract_version": 1},
                  TARGET_ID: {"no_contract": True}}
    if mode == "live":
        with pytest.raises(ValueError, match="Governed"):
            setup_pipeline(execution_mode=mode, sources=[SOURCE], targets=[TARGET],
                selections=selections, context=context, spark_session=spark_session, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52")
        assert_testing_mutations_are_diagnostics_only(spies)
        return
    plan = setup_pipeline(execution_mode=mode, sources=[SOURCE], targets=[TARGET],
                          selections=selections, context=context, spark_session=spark_session, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52")
    bad = spark_session.createDataFrame([(None,)], "id long")
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **kw: bad)
    source = read(plan, spark_session)
    result = write(plan, source, spark_session)
    assert not result["validation_passed"] and not result["published"]
    assert {row["table_id"] for row in plan.results} == {SOURCE_ID}
    assert shared.finalize_pipeline_run(plan)["status"] == "failed"
    assert_testing_mutations_are_diagnostics_only(spies)



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
        monkeypatch.setattr(orchestrator, "schedule_table_profiling", lambda *args, **kw: {"row_count": 2})
    result = write(plan, read(plan, spark_session), spark_session)
    assert result["published"] is (mode == "live")
    assert all(row.get("guardrail_type") == "schema" for row in result["source_guardrail_results"])
    assert all(row.get("guardrail_type") == "schema" for row in plan.results)
    assert "coverage_result" not in result
    assert not any("Coverage" in stage["stage"] for stage in result["orchestration_stages"])
    assert [row["contract_payload_json"] for row in rows] == originals
    if mode == "testing":
        assert result["validation_passed"]
        assert_testing_mutations_are_diagnostics_only(spies)


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
        assert_testing_mutations_are_diagnostics_only(spies)
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
        monkeypatch.setattr(orchestrator, "schedule_table_profiling", lambda *args, **kw: {"row_count": 1})
    source = read(plan, spark_session)
    result = write(plan, source, spark_session, dataframe=spark_session.createDataFrame([(None,)], "id long"))
    assert result["dq_result"]["status"] == "warning"
    assert result["dq_result"]["can_continue"]
    assert result["published"] is (mode == "live")
    if mode == "testing":
        assert result["validation_passed"]
        assert_testing_mutations_are_diagnostics_only(spies)


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
    with pytest.raises(ValueError, match="Duplicate operation"):
        read(plan, spark_session)
    with pytest.raises(RuntimeError, match="previously failed"):
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
    rows = shared.contract_guardrail_rows({**payload["contract"], "contract_payload": payload}, workspace_id="dev", table_id=TARGET_ID)
    assert json.loads(rows[0]["rule_parameters_json"])["data_types"] == {column_name: "bigint"}
    assert json.dumps(payload, sort_keys=True) == original


def assert_testing_mutations_are_diagnostics_only(spies):
    """Verify business stores and ordinary metadata stay untouched during Testing."""
    for name, spy in spies.items():
        if name == "fabricops_kit.pipeline.shared.write_lakehouse_table":
            for call in spy.call_args_list:
                assert call.args[1] == "METADATA_GUARDRAIL_RESULTS"
        else:
            spy.assert_not_called()


def test_iterable_sources_are_materialized_once_for_evidence_and_execution(runtime, spark_session):
    """Evidence hashing must not consume a generator before Write sees its inputs."""
    make, _, _, _ = runtime
    plan = make(contracted=True)
    source = read(plan, spark_session)
    result = run_pipeline_operation(orchestrate_write, source["dataframe"], plan=plan, sources=(item for item in [source]),
                               **TARGET, write_mode="overwrite", spark_session=spark_session, verbose=False)
    assert len(result["source_guardrail_results"]) == 2
    from fabricops_kit.pipeline.shared import finalize_pipeline_run
    assert finalize_pipeline_run(plan, spark_session=spark_session)["status"] == "incomplete"


def test_test_mode_never_uses_business_publication_path(runtime, spark_session, monkeypatch):
    """Test transformations and Guardrails cannot authorize a business write."""
    make, _, spies, _ = runtime
    plan = make("testing", contracted=True)
    owner = importlib.import_module("fabricops_kit.pipeline.orchestrate_write")
    monkeypatch.setattr(owner, "schedule_table_profiling", lambda *args, **kw: {"row_count": 2})
    with plan:
        result = write(plan, read(plan, spark_session), spark_session)
    assert result["published"] is False and not plan.permits_persistence
    assert spies["fabricops_kit.io.write_lakehouse_table"].call_count == 0


@pytest.mark.parametrize("coverage", ["all", "none", "mixed", "source_only"])
def test_independent_contract_coverage_executes_and_records_every_table(runtime, spark_session, coverage):
    """Three participants retain exact choices and enforce only selected payloads."""
    from fabricops_kit.pipeline.shared import finalize_pipeline_run as finalize_pipeline

    _, rows, spies, context = runtime
    customers = {**SOURCE, "table_name": "customers"}
    customers_id = shared.resolve_physical_table_identity(context["config"], "dev", **customers)["table_id"]
    rows.extend([frozen(SOURCE_ID), frozen(customers_id), frozen(TARGET_ID, version=2)])
    selected = {SOURCE_ID, customers_id, TARGET_ID} if coverage == "all" else (
        {SOURCE_ID, TARGET_ID} if coverage == "mixed" else {SOURCE_ID} if coverage == "source_only" else set())
    choices = {row["table_id"]: {"contract_id": row["contract_id"], "contract_version": row["contract_version"]}
               if row["table_id"] in selected else {"no_contract": True} for row in rows}
    plan = setup_pipeline(execution_mode="testing", sources=[SOURCE, customers], targets=[TARGET],
                          selections=choices, pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", context=context, spark_session=spark_session)
    source = read(plan, spark_session)
    customer = run_pipeline_operation(orchestrate_read, plan=plan, **customers, spark_session=spark_session,
                                 verbose=False)
    output = spark_session.createDataFrame([(None,)], "id long") if coverage == "source_only" else source["dataframe"]
    result = run_pipeline_operation(orchestrate_write, output, plan=plan, sources=[source, customer], **TARGET,
                               write_mode="overwrite",
                               verbose=False, spark_session=spark_session)
    finalized = finalize_pipeline(plan)
    assert finalized["status"] == "incomplete"
    assert not result["published"] and result["validation_passed"]
    assert json.loads(plan.selections_json) == choices
    bindings = finalized["operations"]
    assert {item["table_id"] for item in bindings} == set(choices)
    for item in bindings:
        table_id = item["table_id"]
        assert {key: item[key] for key in ("contract_id", "contract_version", "payload_sha256")} == ({"contract_id": None, "contract_version": None, "payload_sha256": None} if table_id not in selected else {
            **choices[table_id], "payload_sha256": hashlib.sha256(
                next(row for row in rows if row["table_id"] == table_id)["contract_payload_json"].encode()).hexdigest()})
    assert {row["table_id"] for row in plan.results} == selected
    assert all(row["contract_id"] == choices[row["table_id"]]["contract_id"] for row in plan.results)
    assert len(plan.results) == 2 * len(selected)
    assert_testing_mutations_are_diagnostics_only(spies)
