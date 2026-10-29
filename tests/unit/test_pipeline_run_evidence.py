"""Complete-run evidence with a simulated configured Delta metadata boundary."""

import copy
import json
import sys
from dataclasses import replace
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared
from fabricops_kit.pipeline.shared import finalize_pipeline_run
from fabricops_kit.pipeline.shared import pipeline_physical_bindings, resolve_physical_table_identity


@pytest.fixture
def runtime(monkeypatch):
    """Keep the real journal and persistence logic; simulate only Fabric/Delta I/O."""
    from importlib import metadata
    installed_version = metadata.version
    monkeypatch.setattr(metadata, "version", lambda name: "test-delta-runtime" if name == "delta-spark" else installed_version(name))
    saved, writes = {}, []
    failure = {"enabled": False, "after_commit": False, "read_unavailable": False}

    physical, contracts = {}, []
    from fabricops_kit.activated_pipeline import shared as authority
    monkeypatch.setattr(authority, "metadata_records", lambda table, **kw: contracts if table == "METADATA_DATA_CONTRACT" else [])
    def merge(plan, row, **kwargs):
        if failure["enabled"]:
            raise OSError("credential=never persist this message")
        record = copy.deepcopy(shared.validate_pipeline_run(row))
        physical[row["run_id"]] = copy.deepcopy(record)
        saved[row["run_id"]] = copy.deepcopy(row)
        writes.append(copy.deepcopy(row))
        if failure["after_commit"] and row["status"] == "succeeded":
            raise OSError("final commit acknowledgement lost")
        plan.evidence["persisted_run_row"] = copy.deepcopy(record)
    monkeypatch.setattr(shared, "_merge_pipeline_run_row", merge)
    monkeypatch.setattr(shared, "get_spark_session", lambda supplied=None, *_args, **_kwargs: SimpleNamespace(conf=SimpleNamespace(get=lambda name: 'test-setting'), createDataFrame=lambda rows, schema=None: SimpleNamespace(row=rows[0])))
    monkeypatch.setattr(shared, "resolve_configured_lakehouse_table", lambda store, table, schema, **kw:
                        (store, table, schema, f"configured/{schema}/{table}"))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kw: {})
    monkeypatch.setattr(shared, "resolve_physical_table_identity", lambda config, active_workspace_id, **kw:
                        {**kw, "table_id": kw["table_name"]})
    monkeypatch.setattr(shared, "pipeline_physical_bindings", lambda identities, **kw: {
        key: {"workspace_id": "workspace", "item_id": item["store"], "kind": "lakehouse", "schema": item.get("schema"), "table_name": item["table_name"]}
        for key, item in identities.items()
    })

    def read_run(*args, **kwargs):
        if failure["read_unavailable"]:
            raise OSError("read unavailable")
        class Rows:
            def filter(self, expression):
                self.run_id = expression.split("'")[1]
                return self
            def limit(self, count):
                return self
            def collect(self):
                return [copy.deepcopy(physical[self.run_id])] if self.run_id in physical else []
        return Rows()
    monkeypatch.setattr(shared, "read_lakehouse_table", read_run)

    def make(mode="live", roles=("source", "source", "target", "target"), activity="fabric-activity", notebook_name="notebook"):
        identities = {f"table{i}": {"table_id": f"table{i}", "store": "Bronze" if role == "source" else "Silver", "table_name": f"table{i}",
                                   "schema": "physical", "logical_id": f"asset{i}", "roles": [role]}
                      for i, role in enumerate(roles)}
        plan = shared.PipelineExecutionPlan(mode, "canary", "notebook", f"run-{len(saved)}", json.dumps(identities),
                                            "{}", json.dumps({key: {"table_id": key, "contract_id": "contract-" + key, "contract_version": 1,
                            "status": "frozen", "contract_payload_json": json.dumps({"table": {"table_id": key, "columns": []}})} for key in identities}), {"config": {}, "scope_workspace_id": "canary", "activity_id": activity, "notebook_name": notebook_name,
                            "_pipeline_bindings": {key: {"workspace_id": "workspace", "item_id": item["store"], "kind": "lakehouse", "schema": item.get("schema"), "table_name": item["table_name"]}
                                                   for key, item in identities.items()}},
                                            pipeline_id="orders")
        contracts.extend(item for item in json.loads(plan.contracts_json).values() if item not in contracts)
        if mode == "live":
            preview = replace(plan, execution_mode="testing", evidence={})
            for index in range(len(roles)):
                operation(preview, index)
            plan = replace(plan, approval_id="approved-release", approved_operations_json=json.dumps(shared.persist_pipeline_run(preview)["operations"], default=str))
        shared.persist_pipeline_run(plan)
        return plan

    def operation(plan, index, *, stages=None, **kwargs):
        identity = json.loads(plan.participants_json)[f"table{index}"]
        kwargs.setdefault("read_mode" if identity["roles"] == ["source"] else "write_mode", "full" if identity["roles"] == ["source"] else "overwrite")
        args = {"store": identity["store"], "schema": identity["schema"], "table_name": identity["table_name"], **kwargs}
        if identity["roles"] == ["target"]:
            args.setdefault("sources", [{"table_id": key} for key, item in json.loads(plan.participants_json).items()
                                        if "source" in item["roles"]])
        with shared.PipelineOperation(plan, identity["roles"][0], args) as journal:
            journal.complete(stages or ([{"stage": "Read", "status": "passed"}] if identity["roles"] == ["source"] else [{"stage": "Write", "status": "passed"}, {"stage": "Profile", "status": "passed"}]))

    return make, operation, saved, writes, failure


def test_read_only_and_multiple_inputs_outputs_finalize_once(runtime):
    """Completion requires all operations and explicit finalization; no last-Write inference."""
    make, operation, saved, writes, _ = runtime
    for roles in [("source",), ("source", "source", "target", "target")]:
        plan = make(roles=roles)
        for index in range(len(roles)):
            operation(plan, index)
            assert saved[plan.plan_id]["status"] == "incomplete"
        plan.evidence["boundary_completed"] = True
        result = finalize_pipeline_run(plan)
        assert result["status"] == "succeeded"
        count = len(writes)
        assert finalize_pipeline_run(plan) == result and len(writes) == count
        with pytest.raises(RuntimeError, match="closed"):
            operation(plan, 0)


def test_missing_failed_blocking_duplicate_and_external_failures(runtime):
    """Every way to miss complete execution prevents a qualifying success."""
    make, operation, saved, _, _ = runtime
    plan = make()
    operation(plan, 0)
    assert finalize_pipeline_run(plan)["status"] == "incomplete"
    plan = make(roles=("source",))
    operation(plan, 0, stages=[{"stage": "Schema", "status": "blocked"}])
    assert finalize_pipeline_run(plan)["status"] == "failed"
    plan = make(roles=("source",))
    operation(plan, 0)
    with pytest.raises(ValueError, match="Duplicate"):
        operation(plan, 0)
    assert finalize_pipeline_run(plan)["status"] == "failed"
    plan = make(roles=("source",))
    operation(plan, 0)
    assert finalize_pipeline_run(plan, failed=True)["status"] == "failed"
    assert not any(row["execution_mode"] == "testing" and row["status"] == "succeeded" for row in saved.values())


def test_operation_exception_is_safe_and_unfinalized_success_is_incomplete(runtime):
    """Persist safe failure codes, never connector exception text."""
    make, operation, saved, _, _ = runtime
    plan = make(roles=("source",))
    with pytest.raises(OSError):
        with shared.PipelineOperation(plan, "source", {"store": "Bronze", "schema": "physical", "table_name": "table0"}):
            raise OSError("password=hidden")
    assert saved[plan.plan_id]["status"] == "failed"
    assert "hidden" not in json.dumps(saved[plan.plan_id], default=str)
    assert finalize_pipeline_run(plan)["status"] == "failed"
    plan = make(roles=("source",))
    operation(plan, 0)
    assert saved[plan.plan_id]["status"] == "incomplete"


@pytest.mark.parametrize("point", ["start", "operation", "finalize"])
def test_evidence_write_failures_poison_the_plan(runtime, point):
    """Failed writes cannot be retried into success on the same run ID."""
    make, operation, saved, _, failure = runtime
    plan = make(roles=("source",))
    if point == "finalize":
        operation(plan, 0)
    failure["enabled"] = True
    with pytest.raises(RuntimeError, match="persistence failed"):
        if point == "start":
            make()
        elif point == "operation":
            operation(plan, 0)
        else:
            finalize_pipeline_run(plan)
    failure["enabled"] = False
    with pytest.raises(RuntimeError, match="persistence failed"):
        if point == "start":
            # Failure during setup returns no usable plan; the preceding run is independent.
            failure["enabled"] = True
            make()
        else:
            finalize_pipeline_run(plan)
    assert not any(row["execution_mode"] == "testing" and row["status"] == "succeeded" for row in saved.values())


@pytest.mark.parametrize("mode,status", [("testing", "succeeded")])
def test_testing_completion_requires_no_executable_identity(runtime, mode, status):
    """Bootstrap is honest initial publication, never Testing activation evidence."""
    make, operation, _, _, _ = runtime
    plan = make(mode=mode, roles=("source",))
    operation(plan, 0)
    plan.evidence["boundary_completed"] = True
    result = finalize_pipeline_run(plan)
    assert result["status"] == status


def test_run_retains_only_enforced_settings_and_exact_contract_references(runtime):
    """Unused parameters and raw SQL never become a second configuration store."""
    make, operation, _, _, _ = runtime
    plan = make(mode="testing", roles=("source",))
    operation(plan, 0, read_mode="full", query="SELECT * FROM orders", read_parameters={"password": "hidden-secret"}, dq_diagnostics="full")
    row = shared.persist_pipeline_run(plan)
    item = row["operations"][0]
    assert item["table_id"] == "table0" and item["contract_id"] == "contract-table0" and item["contract_version"] == 1
    assert item["read_mode"] == "full" and item["query_sha256"]
    assert "hidden-secret" not in json.dumps(row, default=str) and "SELECT" not in json.dumps(row, default=str)
    assert {"configuration", "configuration_json", "configuration_sha256", "read_parameters", "dq_diagnostics"}.isdisjoint(item)
    assert {"candidate_json", "candidate_fingerprint", "definition_id"}.isdisjoint(row)


@pytest.mark.parametrize("parameter,value", [("read_mode", "incremental"), ("query", "SELECT id FROM orders"), ("target_table_id", "table0")])
def test_live_rejects_changed_material_settings_before_operation(runtime, parameter, value):
    """A changed mode, SQL read or incremental target cannot enter a Live operation."""
    make, operation, _, _, _ = runtime
    plan = make(roles=("source",))
    with pytest.raises(ValueError, match="activated authority"):
        operation(plan, 0, **{parameter: value})


def test_live_allows_diagnostic_settings_without_persisting_them(runtime):
    """Diagnostics are not a pipeline approval policy."""
    make, operation, _, _, _ = runtime
    plan = make(roles=("source",))
    operation(plan, 0, read_mode=" FULL ", dq_diagnostics="full", verbose=True)
    assert "dq_diagnostics" not in json.dumps(shared.persist_pipeline_run(plan), default=str)


def test_failed_guardrail_persistence_links_diagnostics_but_cannot_qualify(runtime, monkeypatch):
    """A partial diagnostic append failure leaves the run failed, never successful."""
    make, _, saved, _, _ = runtime
    plan = make(roles=("source",))
    def write(frame, table, **kwargs):
        assert table == "METADATA_GUARDRAIL_RESULTS"
        assert frame.row["run_id"] == plan.plan_id
        assert kwargs["store"] == "Metadata" and kwargs["schema"] == "engineering"
        raise OSError("private diagnostic transport failure")
    monkeypatch.setattr(shared, "write_lakehouse_table", write)
    with pytest.raises(OSError):
        with shared.PipelineOperation(plan, "source", {"store": "Bronze", "schema": "physical", "table_name": "table0"}):
            shared.write_guardrail_result_row(
                spark_session=shared.get_spark_session(), config={}, active_workspace_id="canary", run_id="wrong-run",
                dataset_name="demo", table_name="table0", store_type="lakehouse", layer="Bronze",
                guardrail_type="schema", rule_type="required_columns", table_id="table0",
                result={"guardrail_rule_id": "schema-rule", "guardrail_version": 1, "can_continue": True,
                        "status": "passed", "rule_context": {"guardrail_type": "schema"}},
                context={**plan.runtime_context, "execution_plan": plan})
    assert plan.results[0]["run_id"] == plan.plan_id
    assert finalize_pipeline_run(plan)["status"] == "failed"
    assert saved[plan.plan_id]["status"] != "succeeded"


def test_partial_operation_snapshot_failure_cannot_be_finalized(runtime):
    """Failure after an operation completes retains incomplete persisted state."""
    make, _, saved, _, failure = runtime
    plan = make(roles=("source",))
    with pytest.raises(RuntimeError, match="persistence failed"):
        with shared.PipelineOperation(plan, "source", {"store": "Bronze", "schema": "physical", "table_name": "table0"}) as journal:
            journal.complete([{"stage": "Read", "status": "passed"}])
            failure["enabled"] = True
    failure["enabled"] = False
    with pytest.raises(RuntimeError, match="persistence failed"):
        finalize_pipeline_run(plan)
    assert saved[plan.plan_id]["status"] == "incomplete"


def test_run_schema_has_only_independent_lifecycle_fields():
    """Keep standard audit fields and avoid redundant activation/failure columns."""
    from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
    fields = metadata_table_schema_registry()["METADATA_PIPELINE_RUN"].fieldNames()
    assert len(fields) == 22
    assert fields[0] == "run_id"
    assert {"record_id", "record_type", "snapshot_token", "operation_count", "operations_digest", "operation_summary_json"}.isdisjoint(fields)
    assert {"operations", "approval_id", "profiling", "boundary_completed"} <= set(fields)
    assert fields[-8:] == [name for name, *_ in AUDIT_SCHEMA_FIELDS]


def test_distinct_attempts_keep_activity_identity_and_survive_notebook_rename(runtime, monkeypatch):
    """Preserve the actual activity and stable pipeline across attempts and renames."""
    make, operation, _, _, _ = runtime
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kw: {
        "_activity_id": kw["runtime_context"]["activity_id"],
        "_notebook_id": "physical-notebook", "_notebook_name": kw["runtime_context"]["notebook_name"]})
    runs = []
    diagnostics = []
    monkeypatch.setattr(shared, "write_lakehouse_table", lambda frame, *a, **kw: diagnostics.append(frame.row))
    for name in ("original-notebook", "renamed-notebook"):
        plan = make(roles=("source",), activity="same-fabric-activity", notebook_name=name)
        operation(plan, 0)
        shared.write_guardrail_result_row(
            spark_session=shared.get_spark_session(), config={}, active_workspace_id="canary", run_id="ignored",
            dataset_name="demo", table_name="table0", store_type="lakehouse", layer="Bronze",
            guardrail_type="schema", rule_type="required_columns", table_id="table0",
            result={"guardrail_rule_id": "schema-rule", "guardrail_version": 1, "can_continue": True,
                    "status": "passed", "rule_context": {"guardrail_type": "schema"}},
            context={**plan.runtime_context, "activity_id": plan.plan_id, "execution_plan": plan})
        plan.evidence["boundary_completed"] = True
        result = finalize_pipeline_run(plan)
        assert result["_activity_id"] == "same-fabric-activity" and result["run_id"] != "same-fabric-activity"
        assert result["pipeline_id"] == "orders" and result["_notebook_name"] == name
        runs.append(result["run_id"])
    assert len(set(runs)) == 2
    assert {row["_activity_id"] for row in diagnostics} == {"same-fabric-activity"}
    assert {row["run_id"] for row in diagnostics} == set(runs)


def test_failed_source_iterator_is_a_recorded_write_attempt(runtime):
    """Record generator failures before first Write and after an earlier success."""
    make, operation, _, _, _ = runtime
    for previous_write in (False, True):
        plan = make(roles=("source", "target"))
        operation(plan, 0)
        if previous_write:
            operation(plan, 1)
        def broken_sources():
            raise OSError("private input iterator failure")
            yield {}  # pragma: no cover
        with pytest.raises((OSError, ValueError)):
            with shared.PipelineOperation(plan, "target", {"sources": broken_sources(), "store": "Silver", "schema": "physical", "table_name": "table1", "write_mode": "overwrite"}):
                pytest.fail("Broken source state must fail before publication")
        assert finalize_pipeline_run(plan)["status"] == "failed"


def test_concurrent_duplicate_operations_cannot_both_complete(runtime, monkeypatch):
    """Serialize the duplicate check and reservation even under overlapping attempts."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from unittest.mock import Mock
    make, operation, saved, _, _ = runtime
    plan = make(roles=("source",))
    entered, release, attempted = Event(), Event(), Event()
    real_persist = shared.persist_pipeline_run
    def wait_in_first_operation(plan, **kwargs):
        if not entered.is_set():
            entered.set()
            assert release.wait(5)
        return real_persist(plan, **kwargs)
    monkeypatch.setattr(shared, "persist_pipeline_run", wait_in_first_operation)
    def duplicate():
        attempted.set()
        operation(plan, 0)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(operation, plan, 0)
        assert entered.wait(5)
        second = pool.submit(duplicate)
        assert attempted.wait(5)
        release.set()
        first.result(timeout=5)
        with pytest.raises(ValueError, match="Duplicate"):
            second.result(timeout=5)
    assert finalize_pipeline_run(plan)["status"] == "failed"
    assert saved[plan.plan_id]["status"] == "failed"


def test_finalization_waits_for_an_in_flight_operation(runtime, monkeypatch):
    """Do not seal an incomplete snapshot while an operation is finishing."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    make, operation, _, _, _ = runtime
    plan = make(roles=("source",))
    entered, release = Event(), Event()
    real_persist = shared.persist_pipeline_run
    def wait_in_operation(plan, **kwargs):
        if not entered.is_set():
            entered.set()
            assert release.wait(5)
        return real_persist(plan, **kwargs)
    monkeypatch.setattr(shared, "persist_pipeline_run", wait_in_operation)
    with ThreadPoolExecutor(max_workers=2) as pool:
        active = pool.submit(operation, plan, 0)
        assert entered.wait(5)
        plan.evidence["boundary_completed"] = True
        final = pool.submit(finalize_pipeline_run, plan)
        release.set()
        active.result(timeout=5)
        assert final.result(timeout=5)["status"] == "succeeded"


def test_lost_final_commit_acknowledgement_confirms_exact_durable_snapshot(runtime):
    """The committed Delta transaction, not its transport acknowledgement, is authority."""
    make, operation, saved, _, failure = runtime
    plan = make(roles=("source",))
    operation(plan, 0)
    failure["after_commit"] = True
    plan.evidence["boundary_completed"] = True
    result = finalize_pipeline_run(plan)
    assert result == saved[plan.plan_id] and result["status"] == "succeeded"
    assert not plan.evidence["persistence_failed"] and plan.evidence["sealed"]
    assert finalize_pipeline_run(plan) == result


def test_unreachable_readback_reports_unknown_client_outcome(runtime):
    """An unavailable acknowledgement/read-back cannot undo the committed transaction."""
    make, operation, saved, _, failure = runtime
    plan = make(roles=("source",))
    operation(plan, 0)
    plan.evidence["boundary_completed"] = True
    failure.update(after_commit=True, read_unavailable=True)
    with pytest.raises(RuntimeError, match="outcome is unknown"):
        finalize_pipeline_run(plan)
    assert plan.evidence["persistence_failed"] and not plan.evidence["sealed"]
    assert saved[plan.plan_id]["status"] == "succeeded"
    with pytest.raises(RuntimeError, match="persistence failed"):
        finalize_pipeline_run(plan)




def test_secondary_metadata_failure_preserves_original_publication_details(runtime):
    """Do not erase an earlier committed publication when diagnostics also fail."""
    make, _, _, _, failure = runtime
    plan = make(mode="live", roles=("target",))
    with pytest.raises(RuntimeError) as raised:
        with shared.PipelineOperation(plan, "target", {"store": "Silver", "schema": "physical", "table_name": "table0", "sources": []}):
            error = RuntimeError("Profile failed")
            error.published = True
            error.table_id = "table0"
            error.write_metrics = {"rows_committed": 10}
            error.failed_stage = "Profile"
            failure["enabled"] = True
            raise error
    assert raised.value.published and raised.value.table_id == "table0"
    assert raised.value.write_metrics == {"rows_committed": 10}
    assert raised.value.failed_stage == "Profile"


def test_post_publication_evidence_failure_retains_published_flag(runtime):
    """An evidence error cannot imply that an already completed Write rolled back."""
    make, operation, _, _, failure = runtime
    plan = make(mode="live", roles=("target",))
    with pytest.raises(RuntimeError) as raised:
        with shared.PipelineOperation(plan, "target", {"store": "Silver", "schema": "physical", "table_name": "table0", "sources": []}) as journal:
            journal.complete([{"stage": "Write", "status": "passed"}, {"stage": "Profile", "status": "passed"}])
            failure["enabled"] = True
    assert raised.value.published is True and raised.value.failed_stage == "Run evidence"






@pytest.mark.parametrize("role", ["source", "target"])
@pytest.mark.parametrize("mode", ["testing", "live"])
def test_operation_cannot_switch_to_case_alias_store_in_another_physical_item(runtime, monkeypatch, role, mode):
    """Logical ID normalization cannot authorize an untested physical destination."""
    from fabricops_kit.config.shared import FabricStore
    from tests.helpers import framework_config

    make, _, saved, _, _ = runtime
    config = framework_config()
    config.path_config.paths["dev"]["silver"] = FabricStore(
         workspace_id="dev", item_id="live-item", kind="lakehouse",
    )
    declared = resolve_physical_table_identity(config, "dev", store="Silver", schema=None, table_name="employees")
    actual = resolve_physical_table_identity(config, "dev", store="silver", schema=None, table_name="employees")
    assert declared["table_id"] == actual["table_id"]
    identities = {declared["table_id"]: {**declared, "logical_id": "employees", "roles": [role]}}
    bindings = pipeline_physical_bindings(identities, config=config, workspace_id="dev")
    assert bindings != pipeline_physical_bindings({actual["table_id"]: actual}, config=config, workspace_id="dev")
    original = make(roles=(role,))
    contracts = {declared["table_id"]: json.loads(original.contracts_json)["table0"]}
    plan = replace(original, execution_mode=mode, workspace_id="dev", participants_json=json.dumps(identities),
                   contracts_json=json.dumps({key: None for key in contracts}), evidence={}, approved_operations_json="[]",
                   runtime_context={"config": config, "scope_workspace_id": "dev", "_pipeline_bindings": bindings})
    monkeypatch.setattr(shared, "resolve_physical_table_identity", resolve_physical_table_identity)
    monkeypatch.setattr(shared, "pipeline_physical_bindings", pipeline_physical_bindings)
    with pytest.raises(ValueError, match="physical destination"):
        with plan:
            with shared.PipelineOperation(plan, role, {"store": "silver", "schema": None, "table_name": "employees", "sources": []}):
                pytest.fail("A mismatched physical operation must never start")
    assert (saved[plan.plan_id] if mode == "live" else plan.run_result)["status"] == "failed"


@pytest.mark.parametrize('roles', [('source',), ('source', 'source', 'target', 'target')])
def test_public_finalize_reuses_context_and_is_idempotent(runtime, roles):
    """The explicit notebook end boundary consolidates results without extra work."""
    from fabricops_kit.pipeline.shared import finalize_pipeline_run as finalize_pipeline
    make, operation, saved, writes, _ = runtime
    plan = make(roles=roles)
    for index in range(len(roles)):
        operation(plan, index)
    assert saved[plan.plan_id]['status'] == 'incomplete'
    plan.evidence["boundary_completed"] = True
    result = finalize_pipeline(plan)
    assert result['status'] == 'succeeded'
    assert result['boundary_completed']
    count = len(writes)
    assert finalize_pipeline(plan) == result and len(writes) == count


@pytest.mark.parametrize('failure', ['missing_operation', 'project_exception'])
def test_public_finalize_cannot_approve_incomplete_or_failed_runs(runtime, failure):
    """Manual completion preserves operation coverage and caught project failures."""
    from fabricops_kit.pipeline.shared import finalize_pipeline_run as finalize_pipeline
    make, operation, saved, _, _ = runtime
    plan = make(roles=('source', 'target'))
    operation(plan, 0)
    if failure == 'project_exception':
        operation(plan, 1)
    result = finalize_pipeline(plan, failed=failure == 'project_exception')
    assert result['status'] == ('failed' if failure == 'project_exception' else 'incomplete')
    assert saved[plan.plan_id] == result


def test_profiling_outcomes_preserve_run_grain_and_completion_status(runtime):
    """A legitimate skip or independent activity failure cannot overwrite pipeline status."""
    make, operation, saved, _, _ = runtime
    plan = make(roles=('source', 'target'))
    events = [{'table_id': 'table0', 'activity': 'standard', 'status': 'skipped', 'reason': 'interval_not_elapsed'},
              {'table_id': 'table1', 'activity': 'frequency', 'status': 'failed', 'reason': 'RuntimeError'}]
    for event in events:
        shared.record_profiling_outcome(event, context={'execution_plan': plan})
    for index in range(2):
        operation(plan, index)
    plan.evidence['boundary_completed'] = True
    result = shared.finalize_pipeline_run(plan)
    assert result['status'] == 'succeeded'
    assert len(saved) == 1
    assert result['profiling'][0]['activity'] == events[0]['activity']


def test_operation_exit_does_not_publish_unconfirmed_profiling_success(runtime, monkeypatch):
    """A failed activity journal write cannot leak through the operation-exit retry."""
    make, _, saved, _, _ = runtime
    plan = make(roles=('source',))
    context = {'execution_plan': plan}
    monkeypatch.setattr(shared, 'profiling_context_key', lambda *args, **kwargs: ('physical', {'table_id': 'table0'}))
    monkeypatch.setattr(shared, 'profiling_completion_history', lambda *args, **kwargs: {})
    monkeypatch.setattr(shared, 'execute_table_profile', lambda **kwargs: {'row_count': 100})
    merge = shared._merge_pipeline_run_row
    failed = []
    def fail_once(plan, row, **kwargs):
        events = row['profiling']
        if not failed and any(event['status'] == 'passed' for event in events):
            failed.append(True)
            raise OSError('transient failure before committing success')
        return merge(plan, row, **kwargs)
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', fail_once)
    with pytest.raises(RuntimeError, match='persistence failed'):
        with shared.PipelineOperation(plan, 'source', {'store': 'Bronze', 'schema': 'physical', 'table_name': 'table0'}):
            shared.schedule_table_profiling('table0', 'read', context=context)
    row = saved[plan.plan_id]
    assert row['status'] == 'failed'
    assert not any(event['status'] == 'passed' for event in row['profiling'])
