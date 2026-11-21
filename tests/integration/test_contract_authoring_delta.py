"""Contract authoring races use real keyed Delta writes and revision-fenced MERGEs."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier, local
from types import SimpleNamespace
from uuid import uuid4
import json

import pytest

from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.io import shared as io

pytestmark = pytest.mark.spark


@pytest.fixture
def authoring_delta(spark_session, tmp_path, monkeypatch):
    """Replace Fabric routing while retaining actual transaction and authoring implementations."""
    pytest.importorskip("delta.tables")
    if "DeltaSparkSessionExtension" not in spark_session.conf.get("spark.sql.extensions", ""):
        pytest.skip("requires Delta Spark extensions")
    table = contracts.DATA_CONTRACT_TABLE
    path = str(tmp_path / table)
    spark_session.createDataFrame([], metadata_table_schema_registry()[table]).write.format("delta").option(
        "delta.isolationLevel", "Serializable").save(path)
    catalogue = [{"table_id": "orders", "asset_type": "TABLE", "asset_workspace_id": "DEV",
                  "columns_json": [], "table_name": "orders", "is_active": True}]
    def read(name, **kwargs):
        return catalogue if name == "METADATA_DATA_CATALOGUE" else spark_session.read.format("delta").load(path)
    def write(frame, *args, **kwargs):
        io.write_metadata_frame(frame, path, table)
    def audit(**kwargs):
        return {name: datetime.now() if name == "_committed_at" else str(uuid4())
                for name, *_ in AUDIT_SCHEMA_FIELDS}
    monkeypatch.setattr(contracts, "read_lakehouse_table", read)
    monkeypatch.setattr(contracts, "write_lakehouse_table", write)
    monkeypatch.setattr(contracts, "metadata_table_physical_schema", lambda *args: "governance")
    monkeypatch.setattr(contracts, "build_runtime_audit_fields", audit)
    monkeypatch.setattr(io, "resolve_configured_lakehouse_table", lambda *a, **kw: (None, table, "governance", path))
    kwargs = dict(config={}, active_workspace_id="DEV", spark_session=spark_session)
    return SimpleNamespace(path=path, read=read, write=write, kwargs=kwargs, spark=spark_session,
        create=lambda: contracts.create_contract_draft(table_id="orders", **kwargs))


def test_concurrent_creators_reopen_one_authoritative_draft(authoring_delta, monkeypatch):
    """Both callers succeed with the winning revision after reading the same empty version."""
    r = authoring_delta
    barrier, state = Barrier(2), local()
    def read(table, **kwargs):
        result = r.read(table, **kwargs)
        if table == contracts.DATA_CONTRACT_TABLE:
            result = result.collect()
            if not getattr(state, "read", False):
                state.read = True
                barrier.wait(timeout=30)
        return result
    monkeypatch.setattr(contracts, "read_lakehouse_table", read)
    with ThreadPoolExecutor(2) as pool:
        drafts = list(pool.map(lambda _: r.create(), range(2)))
    assert drafts[0] == drafts[1]
    assert drafts[0]["contract_version"] == 1
    assert r.read(contracts.DATA_CONTRACT_TABLE).count() == 1


def test_lost_draft_append_acknowledgement_reopens_without_replaying(authoring_delta, monkeypatch):
    """Readback resolves an ambiguous creation response without a second append."""
    r = authoring_delta
    calls = []
    def write(*args, **kwargs):
        calls.append(1)
        r.write(*args, **kwargs)
        raise OSError("lost acknowledgement")
    monkeypatch.setattr(contracts, "write_lakehouse_table", write)
    assert r.create()["status"] == "draft"
    assert len(calls) == 1
    assert r.read(contracts.DATA_CONTRACT_TABLE).count() == 1


@pytest.mark.parametrize("change_payload", [True, False])
def test_stale_freeze_preserves_newer_saved_revision(authoring_delta, change_payload):
    """A stale author cannot freeze an older payload; reloading permits the exact current revision."""
    r = authoring_delta
    draft = r.create()
    payload = json.loads(draft["contract_payload_json"])
    if change_payload:
        payload["table"]["table_name"] = "newer authored definition"
    saved = contracts.save_contract_draft(draft=draft, payload=payload, **r.kwargs)
    with pytest.raises(RuntimeError, match="changed in another session"):
        contracts.freeze_contract(draft=draft, **r.kwargs)
    stored = r.read(contracts.DATA_CONTRACT_TABLE).first().asDict()
    assert stored["status"] == "draft"
    assert stored["contract_payload_json"] == saved["contract_payload_json"]
    frozen = contracts.freeze_contract(draft=saved, **r.kwargs)
    assert frozen["contract"]["status"] == "frozen"
    assert frozen["payload"]["table"]["table_name"] == payload["table"]["table_name"]
