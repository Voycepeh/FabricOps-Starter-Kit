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
