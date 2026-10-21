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

    class Merge:
        def alias(self, name):
            return self

        def merge(self, frame, condition):
            assert condition == "target.run_id = source.run_id"
            self.row = frame.row
            return self

        def whenMatchedUpdateAll(self):
            return self

        def whenNotMatchedInsertAll(self):
            return self

        def execute(self):
            if failure["enabled"]:
                raise OSError("credential=never persist this message")
            row = copy.deepcopy(self.row)
            writes.append(row)
            saved[row["run_id"]] = row
            if failure["after_commit"] and row["status"] == "succeeded":
                raise OSError("final commit acknowledgement lost")

    delta = SimpleNamespace(forPath=lambda spark, path: Merge())
    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=delta))
    monkeypatch.setattr(shared, "get_spark_session", lambda supplied=None: SimpleNamespace(conf=SimpleNamespace(get=lambda name: "test-setting"),
        createDataFrame=lambda rows, schema=None: SimpleNamespace(row=rows[0], alias=lambda name: SimpleNamespace(row=rows[0]))))
    monkeypatch.setattr(shared, "resolve_configured_lakehouse_table", lambda store, table, schema, **kw:
                        (store, table, schema, f"configured/{schema}/{table}"))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kw: {})
    monkeypatch.setattr(shared, "resolve_physical_table_identity", lambda config, env, **kw:
                        {**kw, "table_id": kw["table_name"]})
    monkeypatch.setattr(shared, "pipeline_physical_bindings", lambda identities, **kw: {
        key: {"store": item["store"], "schema": item.get("schema"), "table_name": item["table_name"]}
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
                return [copy.deepcopy(saved[self.run_id])] if self.run_id in saved else []
        return Rows()
    monkeypatch.setattr(shared, "read_lakehouse_table", read_run)

    def make(mode="testing", roles=("source", "source", "target", "target"), activity="fabric-activity", notebook_name="notebook"):
        identities = {f"table{i}": {"table_id": f"table{i}", "store": "Bronze" if role == "source" else "Silver", "table_name": f"table{i}",
                                   "schema": "physical", "logical_id": f"asset{i}", "roles": [role]}
                      for i, role in enumerate(roles)}
        plan = shared.PipelineExecutionPlan(mode, "canary", "notebook", f"run-{len(saved)}", json.dumps(identities),
                                            "{}", json.dumps({key: {"table_id": key, "contract_id": "contract-" + key, "contract_version": 1,
                            "contract_payload_json": json.dumps({"table": {"table_id": key, "columns": []}})} for key in identities}), {"config": {}, "env": "canary", "activity_id": activity, "notebook_name": notebook_name,
                            "_pipeline_bindings": {key: {"store": item["store"], "schema": item.get("schema"), "table_name": item["table_name"]}
                                                   for key, item in identities.items()}},
                                            pipeline_id="orders")
        shared.persist_pipeline_run(plan)
        return plan

    def operation(plan, index, *, stages=None, **kwargs):
        identity = json.loads(plan.participants_json)[f"table{index}"]
        args = {"store": identity["store"], "schema": identity["schema"], "table_name": identity["table_name"], **kwargs}
        if identity["roles"] == ["target"]:
            args.setdefault("sources", [{"table_id": key} for key, item in json.loads(plan.participants_json).items()
                                        if "source" in item["roles"]])
        with shared.PipelineOperation(plan, identity["roles"][0], args) as journal:
            journal.complete(stages or [{"stage": "Read" if identity["roles"] == ["source"] else "Processing", "status": "passed"}])

    return make, operation, saved, writes, failure


def test_read_only_and_multiple_inputs_outputs_finalize_once(runtime):
    """Completion requires all operations and explicit finalization; no last-Write inference."""
    make, operation, saved, writes, _ = runtime
    for roles in [("source",), ("source", "source", "target", "target")]:
        plan = make(roles=roles)
        for index in range(len(roles)):
            operation(plan, index)
            assert saved[plan.plan_id]["status"] == "incomplete"
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
    assert "hidden" not in saved[plan.plan_id]["operation_summary_json"]
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
    result = finalize_pipeline_run(plan)
    assert result["status"] == status


def test_candidate_determinism_changes_and_physical_binding_exclusion(runtime):
    """Code, behavior and dependency changes alter identity; routing does not."""
    make, operation, _, _, _ = runtime
    plan = make(roles=("source",))
    operation(plan, 0, read_mode="full", read_parameters={"b": 2, "a": 1})
    baseline = shared.pipeline_candidate(plan)[1]
    assert shared.canonical_candidate_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'
    identities = json.loads(plan.participants_json)
    identities["table0"].update(schema="other", store="elsewhere", table_name="renamed")
    assert shared.pipeline_candidate(replace(plan, environment="other", participants_json=json.dumps(identities)))[1] == baseline
    other = make(roles=("source",))
    operation(other, 0, read_mode="incremental", read_parameters={"a": 1, "b": 2})
    assert shared.pipeline_candidate(other)[1] != baseline
    with pytest.raises(ValueError):
        shared.canonical_candidate_json({"nan": float("nan")})


def test_contract_payload_and_exact_hash_are_retained(runtime):
    """Frozen revisions and semantic payload edits change candidates and exact hashes."""
    make, operation, _, _, _ = runtime
    plan = make(roles=("source",))
    operation(plan, 0)
    payload = '{"table":{"columns":[{"name":"id","data_type":"int"}]}}'
    contract = {"contract_id": "frozen", "contract_version": 1, "contract_payload_json": payload}
    first = replace(plan, contracts_json=json.dumps({"table0": contract}))
    before = shared.pipeline_candidate(first)
    contract["contract_payload_json"] = payload.replace('"int"', '"long"')
    after = shared.pipeline_candidate(replace(plan, contracts_json=json.dumps({"table0": contract})))
    assert before[1] != after[1] and before[2][0]["contract"]["payload_sha256"] != after[2][0]["contract"]["payload_sha256"]


@pytest.mark.parametrize("secret_key", ["password", "api_key", "authorization"])
def test_secret_inputs_and_unidentified_dependencies_cannot_qualify(runtime, secret_key):
    """Secrets never enter run payloads; mappings and SQL need future identity support."""
    make, operation, saved, _, _ = runtime
    plan = make(roles=("source",))
    with pytest.raises(ValueError, match="secrets"):
        operation(plan, 0, read_parameters={secret_key: "hidden-secret"})
    assert "hidden-secret" not in json.dumps(saved[plan.plan_id], default=str)
    assert finalize_pipeline_run(plan)["status"] == "failed"
    plan = make(roles=("source",))
    operation(plan, 0, query="SELECT * FROM externally_bound_table")
    assert finalize_pipeline_run(plan)["status"] == "incomplete"


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
                spark_session=shared.get_spark_session(), config={}, env="canary", run_id="wrong-run",
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
    assert fields == ["run_id", "activated_pipeline_id", "pipeline_id", "execution_mode", "environment_name", "started_at", "completed_at",
                      "status", "candidate_fingerprint", "candidate_json", "operation_summary_json",
                      *[name for name, *_ in AUDIT_SCHEMA_FIELDS]]
    assert len(fields) == 19


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
            spark_session=shared.get_spark_session(), config={}, env="canary", run_id="ignored",
            dataset_name="demo", table_name="table0", store_type="lakehouse", layer="Bronze",
            guardrail_type="schema", rule_type="required_columns", table_id="table0",
            result={"guardrail_rule_id": "schema-rule", "guardrail_version": 1, "can_continue": True,
                    "status": "passed", "rule_context": {"guardrail_type": "schema"}},
            context={**plan.runtime_context, "activity_id": plan.plan_id, "execution_plan": plan})
        result = finalize_pipeline_run(plan)
        assert result["_activity_id"] == "same-fabric-activity" and result["run_id"] != "same-fabric-activity"
        assert result["pipeline_id"] == "orders" and result["_notebook_name"] == name
        runs.append(result["run_id"])
    assert len(set(runs)) == 2
    assert {row["_activity_id"] for row in diagnostics} == {"same-fabric-activity"}
    assert {row["run_id"] for row in diagnostics} == set(runs)


def test_failed_source_iterator_is_a_recorded_write_attempt(runtime):
    """Record generator failures before first Write and after an earlier success."""
    from fabricops_kit import orchestrate_write
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
            orchestrate_write(None, execution_plan=plan, sources=broken_sources(), store="Silver", schema="physical",
                              table_name="table1", write_mode="overwrite")
        assert finalize_pipeline_run(plan)["status"] == "failed"


def test_concurrent_duplicate_operations_cannot_both_complete(runtime, monkeypatch):
    """Serialize the duplicate check and reservation even under overlapping attempts."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from unittest.mock import Mock
    make, operation, saved, _, _ = runtime
    plan = make(roles=("source",))
    entered, release, attempted = Event(), Event(), Event()
    real_spark = shared.get_spark_session
    def wait_in_first_operation(supplied=None):
        if not entered.is_set():
            entered.set()
            assert release.wait(5)
        return real_spark(supplied)
    monkeypatch.setattr(shared, "get_spark_session", wait_in_first_operation)
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
    real_spark = shared.get_spark_session
    def wait_in_operation(supplied=None):
        if not entered.is_set():
            entered.set()
            assert release.wait(5)
        return real_spark(supplied)
    monkeypatch.setattr(shared, "get_spark_session", wait_in_operation)
    with ThreadPoolExecutor(max_workers=2) as pool:
        active = pool.submit(operation, plan, 0)
        assert entered.wait(5)
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
    result = finalize_pipeline_run(plan)
    assert result == saved[plan.plan_id] and result["status"] == "succeeded"
    assert not plan.evidence["persistence_failed"] and plan.evidence["sealed"]
    assert finalize_pipeline_run(plan) == result


def test_unreachable_readback_reports_unknown_client_outcome(runtime):
    """An unavailable acknowledgement/read-back cannot undo the committed transaction."""
    make, operation, saved, _, failure = runtime
    plan = make(roles=("source",))
    operation(plan, 0)
    failure.update(after_commit=True, read_unavailable=True)
    with pytest.raises(RuntimeError, match="outcome is unknown"):
        finalize_pipeline_run(plan)
    assert plan.evidence["persistence_failed"] and not plan.evidence["sealed"]
    assert saved[plan.plan_id]["status"] == "succeeded"
    with pytest.raises(RuntimeError, match="persistence failed"):
        finalize_pipeline_run(plan)


def test_exact_contract_identity_changes_exact_but_not_portable_fingerprint(runtime):
    """Keep exact frozen identity separate from portable payload identity."""
    make, operation, _, _, _ = runtime
    plan = make(roles=("source",))
    operation(plan, 0)
    contract = {"contract_id": "first", "contract_version": 1, "contract_payload_json": '{"table":{"columns":[]}}'}
    before = shared.pipeline_candidate(replace(plan, contracts_json=json.dumps({"table0": contract})))
    contract["contract_id"] = "second"
    after = shared.pipeline_candidate(replace(plan, contracts_json=json.dumps({"table0": contract})))
    assert before[1] != after[1]
    assert before[0]["portable_fingerprint"] == after[0]["portable_fingerprint"]


def test_secondary_metadata_failure_preserves_original_publication_details(runtime):
    """Do not erase an earlier committed publication when diagnostics also fail."""
    make, _, _, _, failure = runtime
    plan = make(mode="testing", roles=("target",))
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
    plan = make(mode="testing", roles=("target",))
    with pytest.raises(RuntimeError) as raised:
        with shared.PipelineOperation(plan, "target", {"store": "Silver", "schema": "physical", "table_name": "table0", "sources": []}) as journal:
            journal.complete([{"stage": "Write", "status": "passed"}, {"stage": "Profile", "status": "passed"}])
            failure["enabled"] = True
    assert raised.value.published is True and raised.value.failed_stage == "Run evidence"


@pytest.mark.parametrize("key", ["schema", "store", "table_name", "environment_name", "notebook_id"])
def test_project_configuration_keys_never_disappear_as_physical_bindings(runtime, key):
    """Arbitrary project values remain exact even when named like routing fields."""
    make, operation, _, _, _ = runtime
    plan = make(roles=("source",))
    operation(plan, 0)
    before = shared.pipeline_candidate(replace(plan, configuration_json=json.dumps({"transform": [{key: "before"}]})))
    after = shared.pipeline_candidate(replace(plan, configuration_json=json.dumps({"transform": [{key: "after"}]})))
    assert before[1] and before[1] != after[1]
    assert before[0]["project_configuration"] == {"transform": [{key: "before"}]}


@pytest.mark.parametrize("role,parameter", [("source", "read_parameters"), ("target", "write_parameters")])
def test_nested_operation_parameters_remain_exact_while_routing_is_portable(runtime, role, parameter):
    """Only top-level routing arguments are excluded from operation identity."""
    make, operation, _, _, _ = runtime
    fingerprints = []
    for value in ("before", "after"):
        plan = make(roles=(role,))
        operation(plan, 0, **{parameter: {"schema": value, "nested": {"table_name": value}}})
        candidate, fingerprint, _ = shared.pipeline_candidate(plan)
        configuration = candidate["operations"][0]["configuration"]
        assert "schema" not in configuration and "store" not in configuration and "table_name" not in configuration
        assert configuration[parameter] == {"schema": value, "nested": {"table_name": value}}
        fingerprints.append(fingerprint)
    assert fingerprints[0] and fingerprints[0] != fingerprints[1]


@pytest.mark.parametrize("role", ["source", "target"])
@pytest.mark.parametrize("mode", ["testing", "live"])
def test_operation_cannot_switch_to_case_alias_store_in_another_physical_item(runtime, monkeypatch, role, mode):
    """Logical ID normalization cannot authorize an untested physical destination."""
    from fabricops_kit.config.shared import FabricStore
    from tests.helpers import framework_config

    make, _, saved, _, _ = runtime
    config = framework_config()
    config.path_config.paths["dev"]["silver"] = FabricStore(
        env="dev", workspace_id="other-workspace", item_id="live-item", kind="lakehouse",
    )
    declared = resolve_physical_table_identity(config, "dev", store="Silver", schema=None, table_name="employees")
    actual = resolve_physical_table_identity(config, "dev", store="silver", schema=None, table_name="employees")
    assert declared["table_id"] == actual["table_id"]
    identities = {declared["table_id"]: {**declared, "logical_id": "employees", "roles": [role]}}
    bindings = pipeline_physical_bindings(identities, config=config, environment="dev")
    assert bindings != pipeline_physical_bindings({actual["table_id"]: actual}, config=config, environment="dev")
    original = make(roles=(role,))
    contracts = {declared["table_id"]: json.loads(original.contracts_json)["table0"]}
    plan = replace(original, execution_mode=mode, environment="dev", participants_json=json.dumps(identities),
                   contracts_json=json.dumps(contracts), evidence={},
                   runtime_context={"config": config, "env": "dev", "_pipeline_bindings": bindings})
    monkeypatch.setattr(shared, "resolve_physical_table_identity", resolve_physical_table_identity)
    monkeypatch.setattr(shared, "pipeline_physical_bindings", pipeline_physical_bindings)
    with pytest.raises(ValueError, match="physical destination"):
        with plan:
            with shared.PipelineOperation(plan, role, {"store": "silver", "schema": None, "table_name": "employees", "sources": []}):
                pytest.fail("A mismatched physical operation must never start")
    assert saved[plan.plan_id]["status"] == "failed"


@pytest.mark.parametrize('roles', [('source',), ('source', 'source', 'target', 'target')])
def test_public_finalize_reuses_context_and_is_idempotent(runtime, roles):
    """The explicit notebook end boundary consolidates results without extra work."""
    from fabricops_kit import finalize_pipeline
    make, operation, saved, writes, _ = runtime
    plan = make(roles=roles)
    for index in range(len(roles)):
        operation(plan, index)
    assert saved[plan.plan_id]['status'] == 'incomplete'
    result = finalize_pipeline(plan)
    assert result['status'] == 'succeeded'
    assert json.loads(result['operation_summary_json'])['boundary_completed']
    count = len(writes)
    assert finalize_pipeline(plan) == result and len(writes) == count


@pytest.mark.parametrize('failure', ['missing_operation', 'project_exception'])
def test_public_finalize_cannot_approve_incomplete_or_failed_runs(runtime, failure):
    """Manual completion preserves operation coverage and caught project failures."""
    from fabricops_kit import finalize_pipeline
    make, operation, saved, _, _ = runtime
    plan = make(roles=('source', 'target'))
    operation(plan, 0)
    if failure == 'project_exception':
        operation(plan, 1)
    result = finalize_pipeline(plan, failed=failure == 'project_exception')
    assert result['status'] == ('failed' if failure == 'project_exception' else 'incomplete')
    assert saved[plan.plan_id] == result
