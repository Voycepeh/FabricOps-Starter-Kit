"""Only aborted metadata transactions may be retried; business publications stay single-attempt."""
from types import SimpleNamespace
import importlib

import pytest

from fabricops_kit.io.shared import retry_delta_metadata
from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES


@pytest.mark.parametrize('name', ['ConcurrentAppendException', 'ConcurrentWriteException',
    'ConcurrentDeleteReadException', 'ConcurrentDeleteDeleteException', 'ConcurrentTransactionException'])
@pytest.mark.parametrize('wrapped', [False, True])
def test_retry_known_delta_conflicts_with_backoff(monkeypatch, name, wrapped):
    """Support both captured Python Delta exceptions and their JVM equivalents."""
    calls, delays = [], []
    monkeypatch.setattr('time.sleep', delays.append)
    def action():
        calls.append(1)
        if len(calls) < 3:
            error = type(name, (Exception,), {})()
            if wrapped:
                error = Exception()
                error.java_exception = SimpleNamespace(getClass=lambda: SimpleNamespace(getSimpleName=lambda: name))
            raise error
        return 'committed'
    assert retry_delta_metadata(action) == 'committed'
    assert len(calls) == 3 and len(delays) == 2 and all(0.1 <= x <= 0.4 for x in delays)


@pytest.mark.parametrize('error', [PermissionError('403'), OSError('lost acknowledgement'),
    ValueError('stale approval'), RuntimeError('DELTA_CONCURRENT_APPEND in arbitrary text')])
def test_unknown_or_stale_failure_is_never_replayed(error):
    """Never infer an aborted commit from exception messages or retry stale decisions."""
    calls = []
    def action():
        calls.append(1)
        raise error
    with pytest.raises(type(error)):
        retry_delta_metadata(action)
    assert len(calls) == 1


def test_metadata_retry_is_bounded(monkeypatch):
    """Persistent contention eventually propagates rather than blocking indefinitely."""
    error = type('ConcurrentAppendException', (Exception,), {})
    calls, delays = [], []
    monkeypatch.setattr('time.sleep', delays.append)
    def action():
        calls.append(1)
        raise error()
    with pytest.raises(error):
        retry_delta_metadata(action)
    assert len(calls) == 32 and len(delays) == 31
    assert all(0.1 <= delay <= 8 for delay in delays)


@pytest.mark.parametrize('table,store,retried', [(table, 'Metadata', True) for table in CANONICAL_METADATA_TABLES] + [('orders', 'Silver', False),
    ('METADATA_GUARDRAIL_RESULTS', 'Silver', False)])
def test_metadata_append_retries_without_replaying_business_writes(monkeypatch, table, store, retried):
    """Canonical table and configured Metadata store must both match before retrying."""
    module = importlib.import_module('fabricops_kit.io.write_lakehouse_table')
    monkeypatch.setattr('time.sleep', lambda _: None)
    monkeypatch.setattr(module, 'validate_dataframe_writer', lambda _: None)
    monkeypatch.setattr(module, 'resolve_configured_lakehouse_table', lambda *a, **kw: (None, table, 'engineering', 'path'))
    monkeypatch.setattr(module, 'repartition_dataframe_for_write', lambda df, _: df)
    calls = []
    def write(*args, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise type('ConcurrentAppendException', (Exception,), {})()
    monkeypatch.setattr(module, 'write_delta_path', write)
    if retried:
        module.write_lakehouse_table(object(), table, store=store, mode='append', verbose=False)
        assert len(calls) == 2
    else:
        with pytest.raises(Exception):
            module.write_lakehouse_table(object(), table, store=store, mode='append', verbose=False)
        assert len(calls) == 1


def test_publication_coordination_is_removed():
    """The single-owner target model does not require runtime Files leases or new tables."""
    from pathlib import Path
    from fabricops_kit.activated_pipeline import shared
    from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES
    assert len(CANONICAL_METADATA_TABLES) == 14
    assert not hasattr(shared, 'publication_claim')
    assert not hasattr(shared, 'release_pipeline_lease')
    assert 'publication_coordination' not in Path(shared.__file__).read_text()


def test_fabric_structured_delta_conflict_is_retried(monkeypatch):
    """Recognize Fabric's DELTA_CONCURRENT_APPEND.WITHOUT_HINT without matching messages."""
    class FabricException(Exception):
        def getErrorClass(self):  # noqa: N802
            return 'DELTA_CONCURRENT_APPEND.WITHOUT_HINT'
    monkeypatch.setattr('time.sleep', lambda _: None)
    calls = []
    def action():
        calls.append(1)
        if len(calls) == 1:
            raise FabricException()
        return True
    assert retry_delta_metadata(action) is True
    assert len(calls) == 2


@pytest.mark.parametrize("destination", [
    "steward", "custom_steward", "agreement", "custom_agreement", "contract", "custom_contract",
])
@pytest.mark.parametrize("failure", ["transient", "exhausted", "permission", "unknown_commit"])
def test_metadata_authoring_destinations_share_one_bounded_retry_budget(monkeypatch, destination, failure):
    """Keep typed input fixed and retry only the append, including configured destinations."""
    from fabricops_kit.data_contract import shared as contracts
    from fabricops_kit.widgets import shared as widgets

    writer = importlib.import_module("fabricops_kit.io.write_lakehouse_table")
    calls, frames, delays, reads, audits = [], [], [], [], []
    monkeypatch.setattr("time.sleep", delays.append)
    monkeypatch.setattr(writer, "validate_dataframe_writer", lambda _: None)
    monkeypatch.setattr(writer, "resolve_configured_lakehouse_table",
        lambda store, table, schema, **kw: (None, table.strip(), schema, "configured-path"))
    monkeypatch.setattr(writer, "repartition_dataframe_for_write", lambda df, _: df)

    class Conflict(Exception):
        def getCondition(self):  # noqa: N802
            return "DELTA_CONCURRENT_APPEND.WITHOUT_HINT"

    error = {"transient": Conflict(), "exhausted": Conflict(),
             "permission": PermissionError("403"), "unknown_commit": OSError("lost acknowledgement")}[failure]

    def write(frame, path, **kwargs):
        calls.append((frame, path, kwargs))
        if failure != "transient" or len(calls) == 1:
            raise error

    def create_frame(rows, schema):
        frame = SimpleNamespace(rows=rows, schema=schema)
        frames.append(frame)
        return frame

    monkeypatch.setattr(writer, "write_delta_path", write)
    spark = SimpleNamespace(createDataFrame=create_frame)
    if "contract" in destination:
        def read(table, **kwargs):
            reads.append((table, kwargs))
            return ([{"table_id": "orders", "workspace_id": "dev", "metadata_level": "table", "is_active": True}]
                    if table == "METADATA_DATA_CATALOGUE" else [])

        def audit(**kwargs):
            audits.append(kwargs)
            return {}

        monkeypatch.setattr(contracts, "read_lakehouse_table", read)
        monkeypatch.setattr(contracts, "build_runtime_audit_fields", audit)
        action = lambda: contracts.create_contract_draft(  # noqa: E731
            table_id="orders", config={}, active_workspace_id="dev", spark_session=spark,
            store="GovernanceArchive" if destination.startswith("custom_") else "Metadata",
            schema="contracts", metadata_workspace_id="metadata-workspace")
    else:
        kind = "data_steward" if "steward" in destination else "data_agreement"
        canonical = "METADATA_DATA_STEWARD" if kind == "data_steward" else "METADATA_DATA_AGREEMENT"
        table = "CUSTOM_" + canonical if destination.startswith("custom_") else canonical
        config = {"metadata_tables": {kind: table}, "governance_metadata_schema": "custom_governance"}
        action = lambda: widgets.write_widget_metadata_row(  # noqa: E731
            spark=spark, config=config, active_workspace_id="dev", table=table,
            row={"steward_id": "steward"} if kind == "data_steward" else {"agreement_id": "agreement"})

    if failure == "transient":
        action()
        assert len(calls) == 2 and len(delays) == 1
    else:
        with pytest.raises(type(error)) as raised:
            action()
        assert raised.value is error
        assert len(calls) == (32 if failure == "exhausted" else 1)
        assert len(delays) == (31 if failure == "exhausted" else 0)
    assert len(frames) == 1
    assert all(frame is frames[0] and path == "configured-path" and options["mode"] == "append"
               for frame, path, options in calls)
    if "contract" in destination:
        assert len(reads) == 2 and len(audits) == 1
        assert all(kwargs["context"]["scope_workspace_id"] == "metadata-workspace" for _, kwargs in reads)
        assert frames[0].rows[0]["contract_version"] == 1
        assert frames[0].rows[0]["status"] == "draft"
    else:
        assert calls[0][2]["options"] is None
