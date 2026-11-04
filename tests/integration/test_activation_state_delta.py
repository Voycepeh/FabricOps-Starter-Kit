"""Real Serializable Delta promotion CAS, replay and phantom detection."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from threading import Barrier
from types import SimpleNamespace
import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
from tests.unit.test_activated_pipeline import promotion

pytestmark = pytest.mark.spark


@pytest.fixture
def authority_delta(monkeypatch, spark_session, tmp_path):
    """Replace only Fabric routing; mutation uses actual Delta transactions."""
    pytest.importorskip("delta.tables")
    if "DeltaSparkSessionExtension" not in spark_session.conf.get("spark.sql.extensions", ""):
        pytest.skip("requires Delta Spark extensions")
    context = {"config": {}, "scope_workspace_id": "DEV", "workspace_id": "DEV", "notebook_id": "notebook"}
    audit = {name: datetime.now() if name == "_committed_at" else "runtime" for name, *_ in AUDIT_SCHEMA_FIELDS}
    paths = {}
    def ensure(table):
        if table not in paths:
            path = str(tmp_path / "Tables" / table)
            spark_session.createDataFrame([], metadata_table_schema_registry()[table]).write.format("delta").option("delta.isolationLevel", "Serializable").save(path)
            paths[table] = path
        return paths[table]
    path = ensure(service.REGISTRY_TABLE)
    # This fixture exercises Delta Registry coordination only; independent approval
    # authorization is covered by test_pipeline_handoff_delta.
    monkeypatch.setattr(service, "verify_registry_approval", lambda *a, **kw: None)
    monkeypatch.setattr(service, "verify_promotion_integrity", lambda *a, **kw: None)
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: (context["config"], context["scope_workspace_id"], context))
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: dict(audit))
    monkeypatch.setattr(service, "metadata_path", lambda table, **kw: ensure(table))
    monkeypatch.setattr(service, "read_lakehouse_table", lambda table, **kw: spark_session.read.format("delta").load(ensure(table)))
    def candidate(version=1, workspace="DEV"):
        return {**promotion(version, workspace), **audit}
    return SimpleNamespace(context=context, spark=spark_session, path=path, ensure=ensure, paths=paths, audit=audit, candidate=candidate)


def test_promotions_preserve_versions_and_reject_stale_review(authority_delta):
    """Verify promotions preserve versions and reject stale review."""
    r = authority_delta
    first = r.candidate()
    assert service.commit_pipeline_promotion(first, expected_active_version=None, context=r.context, spark_session=r.spark)["pipeline_version"] == 1
    service.commit_pipeline_promotion(r.candidate(2), expected_active_version=1, context=r.context, spark_session=r.spark)
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    assert sorted((row["pipeline_version"], row["status"]) for row in rows) == [(1, "superseded"), (2, "active")]
    before = deepcopy(rows)
    with pytest.raises(ValueError, match="Stale"):
        service.commit_pipeline_promotion(r.candidate(3), expected_active_version=1, context=r.context, spark_session=r.spark)
    assert service.read_registry(context=r.context, spark_session=r.spark) == before
    assert service.commit_pipeline_promotion(first, expected_active_version=None, context=r.context, spark_session=r.spark)["status"] == "superseded"


def test_simultaneous_first_promotions_have_one_winner(authority_delta, monkeypatch):
    """Verify simultaneous first promotions have one winner."""
    r, barrier = authority_delta, Barrier(2)
    original = service.replace_metadata_transaction
    def synchronized(*a, **kw):
        barrier.wait(timeout=60)
        return original(*a, **kw)
    monkeypatch.setattr(service, "replace_metadata_transaction", synchronized)
    def promote(suffix):
        row = r.candidate(); row["promotion_id"] += suffix; row["governed_notebook_id"] += suffix
        try:
            service.commit_pipeline_promotion(row, expected_active_version=None, context=r.context, spark_session=r.spark)
            return True
        except Exception:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(promote, ("a", "b"))) == 1
    assert len(service.read_registry(context=r.context, spark_session=r.spark)) == 1


def test_blind_phantom_insert_conflicts_with_tracked_whole_table_read(authority_delta, monkeypatch):
    """An untracked MERGE/append cannot evade the transaction's Serializable read set."""
    r, original = authority_delta, service.replace_metadata_transaction
    def phantom(*a, **kw):
        r.spark.createDataFrame([r.candidate(workspace="OTHER")], metadata_table_schema_registry()[service.REGISTRY_TABLE]).write.format("delta").mode("append").save(r.path)
        return original(*a, **kw)
    monkeypatch.setattr(service, "replace_metadata_transaction", phantom)
    with pytest.raises(Exception):
        service.commit_pipeline_promotion(r.candidate(), expected_active_version=None, context=r.context, spark_session=r.spark)
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    assert len(rows) == 1 and rows[0]["execution_workspace_id"] == "OTHER"


def test_lost_commit_ack_recovers_exact_version_and_replay_adds_no_row(authority_delta, monkeypatch):
    """A successful Delta commit with a lost response is recovered from its exact marker."""
    r, original = authority_delta, service.replace_metadata_transaction
    class LostAcknowledgement:
        def __init__(self, txn): self.txn = txn
        def __getattr__(self, name): return getattr(self.txn, name)
        def commit(self, *args):
            self.txn.commit(*args)
            raise OSError("commit acknowledgement lost")
    def replace(txn, *args, **kwargs):
        return original(LostAcknowledgement(txn), *args, **kwargs)
    monkeypatch.setattr(service, "replace_metadata_transaction", replace)
    row = r.candidate()
    result = service.commit_pipeline_promotion(row, expected_active_version=None, context=r.context, spark_session=r.spark)
    assert result["promotion_id"] == row["promotion_id"]
    again = service.commit_pipeline_promotion(row, expected_active_version=None, context=r.context, spark_session=r.spark)
    assert again["promotion_id"] == result["promotion_id"]
    assert len(service.read_registry(context=r.context, spark_session=r.spark)) == 1


@pytest.fixture
def contract_activation_delta(authority_delta, monkeypatch):
    """Route frozen definitions and identities while retaining real activation/claim Delta writes."""
    import hashlib
    import json
    from fabricops_kit.pipeline import shared as pipeline
    from tests.unit.test_activated_pipeline import operation
    r = authority_delta
    r.ensure(service.ACTIVATION_TABLE)
    payload = json.dumps({"table": {"table_id": "orders", "processing": {"load_strategy": "overwrite"}}})
    contract = {"table_id": "orders", "contract_id": "contract", "contract_version": 1,
        "status": "frozen", "contract_payload_json": payload}
    original = service.metadata_records
    monkeypatch.setattr(service, "metadata_records", lambda table, **kw: [dict(contract)] if table == "METADATA_DATA_CONTRACT" else original(table, **kw))
    monkeypatch.setattr(pipeline, "resolve_catalogue_table_identity", lambda *a, **kw: {"table_id": "orders"})
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda identities, **kw: {"orders": operation(workspace=kw["workspace_id"])["destination"]})
    r.payload_sha256 = hashlib.sha256(payload.encode()).hexdigest()
    return r


def test_exact_contract_activation_is_per_physical_workspace_and_stale_safe(contract_activation_delta):
    """Different physical workspaces select independently; lost-ack retries and stale writes are safe."""
    r = contract_activation_delta
    def activate(workspace, operation_id, expected=None):
        return service.set_table_contract_activation("orders", "contract", 1,
            expected_activation_id=expected, activation_id=operation_id, governance_confirmed=True,
            context={**r.context, "scope_workspace_id": workspace}, spark_session=r.spark)
    first = activate("DEV", "dev-first")
    assert first["payload_sha256"] == r.payload_sha256
    assert activate("DEV", "dev-first")["revision"] == 1
    activate("PROD", "prod-first")
    second = activate("DEV", "dev-next", "dev-first")
    assert second["revision"] == 2
    with pytest.raises(ValueError, match="Stale"):
        activate("DEV", "stale", "dev-first")
    rows = service.read_activations(context=r.context, spark_session=r.spark)
    assert {(row["workspace_id"], row["activation_id"]) for row in rows} == {("DEV", "dev-next"), ("PROD", "prod-first")}
    assert service.read_registry(context=r.context, spark_session=r.spark) == []


def test_contract_activation_cannot_race_existing_unprotected_writer(contract_activation_delta):
    """Activation takes the same physical target claim as publication, never opening an alias gap."""
    from tests.unit.test_activated_pipeline import operation
    r = contract_activation_delta
    service.publication_claim("in-flight-run", operation()["destination"], context=r.context, spark_session=r.spark)
    with pytest.raises(RuntimeError, match="publication lease"):
        service.set_table_contract_activation("orders", "contract", 1, expected_activation_id=None,
            activation_id="new-contract", governance_confirmed=True, context=r.context, spark_session=r.spark)
    assert service.read_activations(context=r.context, spark_session=r.spark) == []


@pytest.mark.parametrize('precondition', ['binding', 'payload'])
def test_contract_activation_rejects_changed_human_review_before_mutation(contract_activation_delta, precondition):
    """Reviewed physical binding and payload hashes are checked before acquiring mutation authority."""
    from tests.unit.test_activated_pipeline import operation
    r = contract_activation_delta
    checks = {'expected_destination': operation(workspace='OTHER')['destination']} if precondition == 'binding' else {'expected_payload_sha256': 'f' * 64}
    with pytest.raises(ValueError, match='changed after review'):
        service.set_table_contract_activation('orders', 'contract', 1, expected_activation_id=None,
            activation_id='reviewed-operation', governance_confirmed=True, context=r.context,
            spark_session=r.spark, **checks)
    assert service.read_activations(context=r.context, spark_session=r.spark) == []


def test_stale_claim_release_preserves_new_owner_and_releases_other_targets(authority_delta):
    """A retried cleanup cannot delete a successor's actual Delta claim or strand another."""
    from tests.unit.test_activated_pipeline import operation
    r = authority_delta
    a, b = (operation(table=name)['destination'] for name in ('A', 'B'))
    for target in (a, b):
        service.publication_claim('old-run', target, context=r.context, spark_session=r.spark)
    service.publication_claim('old-run', a, context=r.context, spark_session=r.spark, release=True)
    service.publication_claim('new-run', a, context=r.context, spark_session=r.spark)
    # Stale/lost-ack cleanup has both targets pending despite the transferred A.
    from types import SimpleNamespace
    plan = SimpleNamespace(plan_id='old-run', runtime_context=r.context,
        evidence={'sealed': True, 'lease_token': 'old-run', 'publication_claims': [a, b]})
    service.release_pipeline_lease(plan, spark_session=r.spark)
    service.publication_claim('third-run', b, context=r.context, spark_session=r.spark)
    with pytest.raises(RuntimeError, match='publication lease'):
        service.publication_claim('third-run', a, context=r.context, spark_session=r.spark)
