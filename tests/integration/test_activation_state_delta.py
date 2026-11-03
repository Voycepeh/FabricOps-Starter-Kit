"""Serializable whole-Registry commits, phantom conflicts and policy leases."""
# ruff: noqa: F811
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from threading import Barrier
from types import SimpleNamespace
import json
import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
from fabricops_kit.pipeline import shared as pipeline
from tests.unit.test_activated_pipeline import contract_candidate, operation, PIPELINE_ID

pytestmark = pytest.mark.spark


@pytest.fixture
def authority_delta(monkeypatch, spark_session, tmp_path):
    """Use actual configured Delta boundaries and replace only Fabric discovery."""
    pytest.importorskip("delta.tables")
    if "DeltaSparkSessionExtension" not in spark_session.conf.get("spark.sql.extensions", ""):
        pytest.skip("requires Delta Spark extensions")
    schemas = metadata_table_schema_registry()
    context = {"config": {}, "scope_workspace_id": "DEV", "workspace_id": "DEV", "notebook_id": "notebook"}
    audit = {name: datetime.now() if name == "_committed_at" else "test-runtime" for name, *_ in AUDIT_SCHEMA_FIELDS}
    audit.update(_workspace_id="DEV", _notebook_id="notebook")
    paths = {}

    def ensure(table):
        if table not in paths:
            path = str(tmp_path / table)
            initial = [{**service.empty_pipeline_authority(), **audit}] if table == service.REGISTRY_TABLE else []
            spark_session.createDataFrame(initial, schemas[table]).write.format("delta").option("delta.isolationLevel", "Serializable").save(path)
            paths[table] = path
        return paths[table]

    path = ensure(service.REGISTRY_TABLE)
    for module in (service, pipeline):
        monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context["config"], context["scope_workspace_id"], context))
        monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kw: dict(audit))
        monkeypatch.setattr(module, "resolve_configured_lakehouse_table", lambda store, table, schema, **kw: (store, table, schema, ensure(table)))
        monkeypatch.setattr(module, "read_lakehouse_table", lambda table, **kw: spark_session.read.format("delta").load(ensure(table)))
    return SimpleNamespace(context=context, spark=spark_session, path=path, ensure=ensure, paths=paths, audit=audit)


def test_stale_registry_commit_leaves_every_record_unchanged(authority_delta):
    """A stale reviewed token cannot partially replace independent activations."""
    r = authority_delta
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    token = service.registry_control(rows)["token"]
    service.commit_registry(rows, expected_token=token, context=r.context, spark_session=r.spark)
    before = service.read_registry(context=r.context, spark_session=r.spark)
    rows.append({**contract_candidate(), **r.audit})
    with pytest.raises(ValueError, match="Stale"):
        service.commit_registry(rows, expected_token=token, context=r.context, spark_session=r.spark, governance_change=True)
    assert service.read_registry(context=r.context, spark_session=r.spark) == before


def test_overlapping_full_table_transactions_cannot_both_publish(authority_delta, monkeypatch):
    """Serializable tracked reads serialize simultaneous activation decisions."""
    r, barrier = authority_delta, Barrier(2)
    original = service.replace_registry_transaction
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    token = service.registry_control(rows)["token"]

    def synchronize(*args, **kwargs):
        barrier.wait(timeout=60)
        return original(*args, **kwargs)

    monkeypatch.setattr(service, "replace_registry_transaction", synchronize)

    def publish(workspace):
        wanted = deepcopy(rows) + [{**contract_candidate(workspace), **r.audit}]
        try:
            return service.commit_registry(wanted, expected_token=token, context=r.context, spark_session=r.spark, governance_change=True)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(publish, ("DEV", "OTHER")))
    assert sum(result is not None for result in results) == 1
    assert len(service.read_registry(context=r.context, spark_session=r.spark)) == 2


def test_blind_append_phantom_conflicts_with_registry_replacement(authority_delta, monkeypatch):
    """An inserted activation cannot be dropped by a transaction's older snapshot."""
    r = authority_delta
    original = service.replace_registry_transaction
    rows = service.read_registry(context=r.context, spark_session=r.spark)

    def insert_phantom(*args, **kwargs):
        r.spark.createDataFrame([{**contract_candidate("OTHER"), **r.audit}],
            metadata_table_schema_registry()[service.REGISTRY_TABLE]).write.format("delta").mode("append").save(r.path)
        return original(*args, **kwargs)

    monkeypatch.setattr(service, "replace_registry_transaction", insert_phantom)
    with pytest.raises(Exception):
        service.commit_registry(rows, expected_token=service.registry_control(rows)["token"], context=r.context, spark_session=r.spark)
    actual = service.read_registry(context=r.context, spark_session=r.spark)
    assert len(actual) == 2 and service.registry_control(actual)["token"] == service.registry_control(rows)["token"]


def test_lost_commit_ack_is_confirmed_from_exact_historical_version(authority_delta, monkeypatch):
    """A committed mutation is not replayed when its acknowledgement is lost."""
    r = authority_delta
    original = service.replace_registry_transaction

    class LostAck:
        def __init__(self, txn):
            self.txn = txn

        def __getattr__(self, key):
            return getattr(self.txn, key)

        def commit(self, *args):
            self.txn.commit(*args)
            raise OSError("acknowledgement lost")

    def lose_ack(txn, *args, **kwargs):
        return original(LostAck(txn), *args, **kwargs)

    monkeypatch.setattr(service, "replace_registry_transaction", lose_ack)
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    old_token = service.registry_control(rows)["token"]
    new_token = service.commit_registry(rows, expected_token=old_token, context=r.context, spark_session=r.spark)
    assert new_token != old_token
    assert service.registry_control(service.read_registry(context=r.context, spark_session=r.spark))["token"] == new_token


def test_missing_control_is_never_reseeded_by_runtime(authority_delta):
    """Corruption cannot be disguised as a fresh authority."""
    from delta.tables import DeltaTable
    r = authority_delta
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    DeltaTable.forPath(r.spark, r.path).delete()
    with pytest.raises(ValueError, match="missing or duplicated"):
        service.commit_registry(rows, expected_token=service.registry_control(rows)["token"], context=r.context, spark_session=r.spark)


def test_policy_lease_pins_target_and_releases_only_completed_run(authority_delta):
    """Ungoverned targets are pinned without changing publication/checkpoint identities."""
    r = authority_delta
    plan = SimpleNamespace(runtime_context=r.context, workspace_id="DEV", pipeline_id=PIPELINE_ID,
        plan_id="run", evidence={})
    service.guard_ungoverned_write(plan, "orders", operation()["destination"], spark_session=r.spark)
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    leases = json.loads(service.registry_control(rows)["leases_json"])
    assert len(leases) == 1 and leases[0]["run_id"] == "run"
    wanted = deepcopy(rows) + [{**contract_candidate(), **r.audit}]
    with pytest.raises(ValueError, match="Drain"):
        service.commit_registry(wanted, expected_token=service.registry_control(rows)["token"],
            context=r.context, spark_session=r.spark, governance_change=True)
    plan.evidence["sealed"] = True
    service.release_pipeline_lease(plan, spark_session=r.spark)
    assert service.registry_control(service.read_registry(context=r.context, spark_session=r.spark))["leases_json"] == "[]"


def frozen_contract(r, monkeypatch):
    """Install a globally frozen Contract and configured physical identity."""
    payload = json.dumps({"contract": {"contract_id": "contract", "contract_version": 1},
        "table": {"table_id": "orders", "columns": [], "processing": {"load_strategy": "overwrite"}},
        "guardrails": []})
    row = dict(contract_id="contract", contract_version=1, table_id="orders", status="frozen",
        evidence_workspace_id="DEV", contract_payload_json=payload, **r.audit)
    r.spark.createDataFrame([row], metadata_table_schema_registry()["METADATA_DATA_CONTRACT"]).write.format(
        "delta").mode("append").save(r.ensure("METADATA_DATA_CONTRACT"))
    monkeypatch.setattr(pipeline, "resolve_catalogue_table_identity", lambda *a, **kw: {"table_id": "orders"})
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: {
        "orders": {**operation()["destination"], "workspace_id": kw["workspace_id"]}})
    return row


def test_contract_activation_is_independent_and_preserves_exact_frozen_payload(authority_delta, monkeypatch):
    """A Contract activates before any pipeline, without copying or altering its payload."""
    r = authority_delta
    frozen = frozen_contract(r, monkeypatch)
    before = service.read_registry(context=r.context, spark_session=r.spark)
    result = service.set_table_contract_activation("orders", "contract", 1,
        expected_token=service.registry_control(before)["token"], governance_confirmed=True,
        context=r.context, spark_session=r.spark)
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    assert result["status"] == "active" and len(rows) == 2
    assert service.resolve_activation_contract(result, context=r.context, spark_session=r.spark)["contract_payload_json"] == frozen["contract_payload_json"]
    assert not any(row["record_type"] == "pipeline_activation" for row in rows)
    control = service.registry_control(rows)
    assert control["last_governance_audit_uri"] and control["last_governance_change_id"]
    plan = SimpleNamespace(runtime_context=r.context, workspace_id="DEV", pipeline_id=PIPELINE_ID, plan_id="blocked", evidence={})
    with pytest.raises(ValueError, match="protected Table ID"):
        service.guard_ungoverned_write(plan, "orders", operation()["destination"], spark_session=r.spark)
    # Frozen status plus Contract activation still grants no consumer Agreement.
    with pytest.raises(ValueError, match="unambiguous active pipeline Agreement"):
        service.resolve_active_consumer_contract({}, "DEV", "orders", spark_session=r.spark)
    after = service.read_registry(context=r.context, spark_session=r.spark)
    with pytest.raises(ValueError, match="Stale"):
        service.set_table_contract_activation("orders", "contract", 1,
            expected_token=service.registry_control(before)["token"], governance_confirmed=True,
            context=r.context, spark_session=r.spark)
    assert service.read_registry(context=r.context, spark_session=r.spark) == after


def test_contract_activation_drains_inflight_ungoverned_target_then_succeeds(authority_delta, monkeypatch):
    """Policy changes and Ungoverned target admission share the control CAS."""
    r = authority_delta
    frozen_contract(r, monkeypatch)
    plan = SimpleNamespace(runtime_context=r.context, workspace_id="DEV", pipeline_id=PIPELINE_ID,
        plan_id="in-flight", evidence={})
    service.guard_ungoverned_write(plan, "orders", operation()["destination"], spark_session=r.spark)
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    with pytest.raises(ValueError, match="Drain"):
        service.set_table_contract_activation("orders", "contract", 1,
            expected_token=service.registry_control(rows)["token"], governance_confirmed=True,
            context=r.context, spark_session=r.spark)
    plan.evidence["sealed"] = True
    service.release_pipeline_lease(plan, spark_session=r.spark)
    token = service.registry_control(service.read_registry(context=r.context, spark_session=r.spark))["token"]
    service.set_table_contract_activation("orders", "contract", 1, expected_token=token,
        governance_confirmed=True, context=r.context, spark_session=r.spark)
    with pytest.raises(ValueError, match="alias"):
        service.guard_ungoverned_write(plan, "renamed-table-id", operation()["destination"], spark_session=r.spark)


def test_contract_activation_and_ungoverned_admission_cannot_both_win(authority_delta, monkeypatch):
    """Actual policy and writer admission actions race in the same Serializable transaction domain."""
    r, barrier = authority_delta, Barrier(2)
    frozen_contract(r, monkeypatch)
    token = service.registry_control(service.read_registry(context=r.context, spark_session=r.spark))["token"]
    plan = SimpleNamespace(runtime_context=r.context, workspace_id="DEV", pipeline_id=PIPELINE_ID,
        plan_id="racing-run", evidence={})
    original = service.replace_registry_transaction

    def synchronize(*args, **kwargs):
        barrier.wait(timeout=60)
        return original(*args, **kwargs)

    monkeypatch.setattr(service, "replace_registry_transaction", synchronize)

    def action(kind):
        try:
            if kind == "contract":
                service.set_table_contract_activation("orders", "contract", 1, expected_token=token,
                    governance_confirmed=True, context=r.context, spark_session=r.spark)
            else:
                service.guard_ungoverned_write(plan, "orders", operation()["destination"], spark_session=r.spark)
            return kind
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(action, ("contract", "writer")))
    assert sum(result is not None for result in results) == 1
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    leases = json.loads(service.registry_control(rows)["leases_json"])
    active = [row for row in rows if row["record_type"] == "table_contract_activation"]
    assert bool(leases) != bool(active)


def test_governance_receipts_chain_and_recover_after_postcommit_failure(authority_delta, monkeypatch):
    """Committed audit proof survives beyond ordinary Delta log retention."""
    from pathlib import Path
    from fabricops_kit.activated_pipeline import migrate_registry as migration
    r = authority_delta
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    wanted = deepcopy(rows) + [{**contract_candidate(), **r.audit}]
    original = service.write_governance_archive

    def fail_receipt(*args, **kwargs):
        if kwargs.get("archive_uri"):
            raise OSError("receipt store unavailable")
        return original(*args, **kwargs)

    monkeypatch.setattr(service, "write_governance_archive", fail_receipt)
    with pytest.raises(OSError, match="receipt store unavailable"):
        service.commit_registry(wanted, expected_token=service.registry_control(rows)["token"],
            context=r.context, spark_session=r.spark, governance_change=True)
    committed = service.read_registry(context=r.context, spark_session=r.spark)
    first = deepcopy(service.registry_control(committed))
    assert len(committed) == 2
    assert not Path(first["last_governance_audit_uri"] + ".committed.json").exists()
    monkeypatch.setattr(service, "write_governance_archive", original)
    # Repeat setup repairs the receipt from exact committed history, without a Registry rewrite.
    migrated, report = migration.migrate_registry(table=r.spark.read.format("delta").load(r.path),
        context=r.context, spark_session=r.spark)
    assert report is None and migrated.collect() == r.spark.read.format("delta").load(r.path).collect()
    assert service.registry_control(service.read_registry(context=r.context, spark_session=r.spark))["token"] == first["token"]
    assert Path(first["last_governance_audit_uri"] + ".committed.json").exists()
    second = deepcopy(committed)
    next(row for row in second if row["record_type"] == "table_contract_activation")["contract_version"] = 2
    service.commit_registry(second, expected_token=first["token"], context=r.context, spark_session=r.spark, governance_change=True)
    current = service.read_registry(context=r.context, spark_session=r.spark)
    control = service.registry_control(current)
    archive = json.loads(Path(control["last_governance_audit_uri"]).read_text())
    assert archive["previous_governance_audit_uri"] == first["last_governance_audit_uri"]
    # Once receipts exist, validation no longer needs retained Delta history.
    from delta.tables import DeltaTable
    monkeypatch.setattr(DeltaTable, "forPath", lambda *args: pytest.fail("committed receipts must survive log retention"))
    service.ensure_registry_audit_receipts(current, path=r.path, spark_session=r.spark)


def test_corrupt_governance_archive_blocks_following_registry_mutation(authority_delta):
    """Audit tampering cannot be hidden by a later control-token update."""
    r = authority_delta
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    service.commit_registry(rows + [{**contract_candidate(), **r.audit}],
        expected_token=service.registry_control(rows)["token"], context=r.context, spark_session=r.spark, governance_change=True)
    current = service.read_registry(context=r.context, spark_session=r.spark)
    control = service.registry_control(current)
    uri = control["last_governance_audit_uri"]
    file = r.spark._jvm.org.apache.hadoop.fs.Path(uri)
    file.getFileSystem(r.spark._jsc.hadoopConfiguration()).delete(file, False)
    service.write_governance_archive({"change_id": "altered", "after": []},
        path=r.path, spark_session=r.spark, archive_uri=uri)
    with pytest.raises(ValueError, match="audit does not match"):
        service.commit_registry(current, expected_token=control["token"], context=r.context, spark_session=r.spark)
    assert service.read_registry(context=r.context, spark_session=r.spark) == current


@pytest.mark.parametrize("alias", [False, True])
def test_contract_activation_uses_stored_foreign_bindings(authority_delta, monkeypatch, alias):
    """Activating DEV needs only DEV configuration, even with a PROD candidate."""
    r = authority_delta
    frozen_contract(r, monkeypatch)
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    foreign = {**contract_candidate("PROD"), **r.audit}
    if alias:
        foreign["destination_json"] = json.dumps(operation()["destination"])
    rows.append(foreign)
    service.commit_registry(rows, expected_token=service.registry_control(rows)["token"],
        context=r.context, spark_session=r.spark, governance_change=True)
    before = service.read_registry(context=r.context, spark_session=r.spark)
    scopes = []

    def bindings(identities, *, config, workspace_id):
        scopes.append(workspace_id)
        assert workspace_id == "DEV"
        return {"orders": operation()["destination"]}

    def identity(config, workspace_id, table_id, *, context, spark_session):
        assert workspace_id == "DEV" and context["scope_workspace_id"] == "CENTRAL"
        return {"table_id": table_id}

    monkeypatch.setattr(pipeline, "resolve_catalogue_table_identity", identity)
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", bindings)
    def activate():
        return service.set_table_contract_activation("orders", "contract", 1,
            expected_token=service.registry_control(before)["token"], governance_confirmed=True,
            context={**r.context, "metadata_workspace_id": "CENTRAL"}, spark_session=r.spark)

    if alias:
        with pytest.raises(ValueError, match="alias one physical destination"):
            activate()
        assert service.read_registry(context=r.context, spark_session=r.spark) == before
    else:
        result = activate()
        assert json.loads(result["destination_json"]) == operation()["destination"]
    assert scopes == ["DEV"]
