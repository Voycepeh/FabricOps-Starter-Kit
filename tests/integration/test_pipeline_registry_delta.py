"""Real Delta uniqueness, stale-token rollback and interrupted-setup recovery."""
# ruff: noqa: F811
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
from fabricops_kit.pipeline import shared
from tests.integration.test_activation_state_delta import authority_delta  # noqa: F401

pytestmark = pytest.mark.spark


@pytest.fixture
def registry_delta(authority_delta, monkeypatch, tmp_path):
    """Route the actual production registry CAS to one seeded Delta table."""
    runtime = authority_delta
    context = {**runtime.context, 'notebook_name': 'Any notebook name'}
    return SimpleNamespace(context=context, spark=runtime.spark, path=runtime.path, audit=runtime.audit)


def test_persisted_registry_recovers_after_setup_stops_and_updates_rename(registry_delta):
    """A binding and its audit update inside the single shared authority row."""
    r = registry_delta
    row = shared.resolve_pipeline_registration(context=r.context, spark_session=r.spark)
    assert UUID(row['pipeline_id']).version == 4
    _token, original = shared.read_pipeline_registry(context=r.context, spark_session=r.spark)
    again = shared.resolve_pipeline_registration(context={**r.context, 'notebook_name': 'Renamed'}, spark_session=r.spark)
    assert again['pipeline_id'] == row['pipeline_id']
    _token, bindings = shared.read_pipeline_registry(context=r.context, spark_session=r.spark)
    assert len(bindings) == 1 and bindings[0]['notebook_name'] == 'Renamed'
    assert bindings[0]['registered_at'] == original[0]['registered_at']
    assert bindings[0]['registered_by'] == original[0]['registered_by']
    assert r.spark.read.format('delta').load(r.path).count() == 1


def test_stale_cas_rolls_back_binding_insert_together_with_control_row(registry_delta):
    """A stale transaction cannot leave an inserted competing registration behind."""
    runtime = registry_delta
    first = shared.resolve_pipeline_registration(context=runtime.context, spark_session=runtime.spark)
    stale = {**first, 'pipeline_id': str(uuid4()), 'notebook_id': 'other-notebook'}
    with pytest.raises(Exception, match='Stale Pipeline Registry'):
        shared.commit_pipeline_registration(stale, expected_token='initial', context=runtime.context, spark_session=runtime.spark)
    _token, bindings = shared.read_pipeline_registry(context=runtime.context, spark_session=runtime.spark)
    assert [row['pipeline_id'] for row in bindings] == [first['pipeline_id']]


def test_concurrent_new_notebook_registration_keeps_one_identity(registry_delta, monkeypatch):
    """Two first-time clients race real Serializable MERGE transactions."""
    runtime = registry_delta
    read = shared.read_pipeline_registry
    ready = Barrier(2)
    def racing_read(**kwargs):
        token, rows = read(**kwargs)
        if token == 'initial':
            ready.wait(timeout=30)
        return token, rows
    monkeypatch.setattr(shared, 'read_pipeline_registry', racing_read)
    def register(_):
        try:
            return shared.resolve_pipeline_registration(context=runtime.context, spark_session=runtime.spark)['pipeline_id']
        except Exception:
            return None  # Losing client retries setup and recovers the committed binding.
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(register, range(2)))
    _token, bindings = read(context=runtime.context, spark_session=runtime.spark)
    assert len(bindings) == 1 and sum(value is not None for value in results) <= 1
    monkeypatch.setattr(shared, 'read_pipeline_registry', read)
    recovered = shared.resolve_pipeline_registration(context=runtime.context, spark_session=runtime.spark)
    assert recovered['pipeline_id'] == bindings[0]['pipeline_id']
