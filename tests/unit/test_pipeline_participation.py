"""Run participation projections and lossless historical reconciliation."""

# ruff: noqa: F811

from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace

import pytest

from fabricops_kit.config.metadata_schemas import (
    AUDIT_SCHEMA_FIELDS, encode_metadata_row, metadata_table_schema_registry,
)
from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401


def _frame(spark, records):
    """Encode actual persisted JSON with complete physical audit fields."""
    rows = []
    for record in records:
        audit = {name: datetime(2026, 11, 20) if kind == 'timestamp' else name
                 for name, kind, _nullable in AUDIT_SCHEMA_FIELDS}
        rows.append(encode_metadata_row('METADATA_PIPELINE_RUN', {**audit, **deepcopy(record)}))
    return spark.createDataFrame(rows, metadata_table_schema_registry()['METADATA_PIPELINE_RUN'])


def test_three_reads_two_writes_and_catalogue_join(runtime, spark_session):
    """Each participant joins to its table observation without column fanout."""
    make, operation, _saved, _writes, _failure = runtime
    plan = make(mode='ungoverned', roles=('source', 'source', 'source', 'target', 'target'))
    for index in range(5):
        operation(plan, index)
    shared.record_pipeline_publication('table3', 'committed', context={'execution_plan': plan})
    row = shared.pipeline_run_row(plan, status='failed')
    participants = shared.pipeline_participation(_frame(spark_session, [row])).cache()
    try:
        records = participants.collect()
        assert len(records) == 5
        assert {r.run_id for r in records} == {plan.plan_id}
        assert sum(r.pipeline_role == 'source' for r in records) == 3
        assert sum(r.pipeline_role == 'target' for r in records) == 2
        assert all(r.run_status == 'failed' and r.operation_status == 'succeeded' for r in records)
        assert next(r for r in records if r.table_id == 'table3').publication_status == 'committed'
        catalogue = spark_session.createDataFrame(
            [('canary', 'table0', 'table'), ('canary', 'table0', 'column'),
             ('different', 'table0', 'table')], ['workspace_id', 'table_id', 'metadata_level'])
        from pyspark.sql import functions as F
        joined = participants.alias('p').join(catalogue.filter("metadata_level = 'table'").alias('c'),
            (F.col('p.table_id') == F.col('c.table_id'))
            & (F.col('p.catalogue_workspace_id') == F.col('c.workspace_id')))
        assert joined.count() == 1
        assert all(r.participant_workspace_id == 'workspace' for r in records)
    finally:
        participants.unpersist()


def test_read_only_and_unstarted_operations(runtime, spark_session):
    """A Read counts without any Write; unstarted declarations do not count."""
    make, operation, *_ = runtime
    plan = make(mode='ungoverned', roles=('source', 'source', 'target'))
    operation(plan, 0)
    row = shared.pipeline_run_row(plan, status='incomplete')
    result = shared.pipeline_participation(_frame(spark_session, [row])).collect()
    assert [(r.table_id, r.pipeline_role) for r in result] == [('table0', 'source')]


def test_publication_before_failure_and_dual_roles(runtime, spark_session):
    """Published targets remain visible when finalization fails; both roles survive."""
    make, operation, *_ = runtime
    plan = make(mode='ungoverned', roles=('source', 'target'))
    operation(plan, 0)
    failure = RuntimeError('metadata finalization failed')
    failure.published = True
    failure.write_metrics = {'rows_committed': 2}
    with pytest.raises(RuntimeError, match='metadata finalization'):
        with shared.PipelineOperation(plan, 'target', {'store': 'Silver', 'schema': 'physical',
                'table_name': 'table1', 'write_mode': 'overwrite', 'sources': [{'table_id': 'table0'}]}):
            raise failure
    row = shared.pipeline_run_row(plan, status='failed')
    assert row['operations'][1]['publication_status'] == 'published'
    row['operations'][1]['table_id'] = 'table0'
    result = shared.pipeline_participation(_frame(spark_session, [row])).collect()
    assert {(r.table_id, r.pipeline_role) for r in result} == {('table0', 'source'), ('table0', 'target')}
    target = next(r for r in result if r.pipeline_role == 'target')
    assert target.operation_status == 'failed' and target.publication_status == 'published'


def test_files_and_legacy_run_hashes(runtime, spark_session):
    """Files reuse their selector key without changing released Run descriptors."""
    make, operation, *_ = runtime
    plan = make(mode='ungoverned', roles=('source',))
    operation(plan, 0)
    row = shared.pipeline_run_row(plan, status='incomplete')
    row['operations'][0].update(source_type='file', source_id='file:example', table_id=None)
    before = shared.canonical_pipeline_json(row)
    result = shared.pipeline_participation(_frame(spark_session, [row])).first()
    assert result.source_id == result.table_id == 'file:example' and result.asset_type == 'FILE'
    assert result.catalogue_workspace_id == result.participant_workspace_id == 'workspace'
    catalogue = spark_session.createDataFrame(
        [('workspace', 'file:example', 'file'), ('canary', 'file:other', 'file')],
        ['workspace_id', 'table_id', 'metadata_level'])
    from pyspark.sql import functions as F
    projected = shared.pipeline_participation(_frame(spark_session, [row])).alias('p')
    assert projected.join(catalogue.alias('c'),
        (F.col('p.table_id') == F.col('c.table_id'))
        & (F.col('p.catalogue_workspace_id') == F.col('c.workspace_id'))).count() == 1
    assert shared.canonical_pipeline_json(row) == before
    assert 'publication_status' not in shared.validate_pipeline_run(shared.pipeline_run_row(plan, status='incomplete'))['operations'][0]


def test_historical_reconciliation_is_read_only_and_never_guesses(runtime, spark_session):
    """Classify unique, ambiguous and absent matches across shared activity IDs."""
    make, operation, *_ = runtime
    plan = make(mode='ungoverned', roles=('source',))
    operation(plan, 0)
    row = shared.pipeline_run_row(plan, status='incomplete')
    row.update(_activity_id='activity', _notebook_id='notebook')
    other = deepcopy(row)
    other['run_id'] = 'second-run'
    other['_activity_id'] = 'ambiguous'
    third = deepcopy(other)
    third['run_id'] = 'third-run'
    rows = [('canary', 'unique', 'activity', 'notebook', 'table0', 'source'),
            ('canary', 'ambiguous', 'ambiguous', 'notebook', 'table0', 'source'),
            ('canary', 'missing', 'no-run', 'notebook', 'table0', 'source'),
            ('other', 'foreign', 'activity', 'notebook', 'table0', 'source'),
            ('canary', 'wrong-notebook', 'activity', 'different', 'table0', 'source')]
    legacy = spark_session.createDataFrame(rows,
        ['workspace_id', 'lineage_id', '_activity_id', '_notebook_id', 'table_id', 'pipeline_role'])
    before = legacy.collect()
    runs = _frame(spark_session, [row, other, third])
    result = {r.lineage_id: r for r in shared.reconcile_pipeline_participation(legacy, runs).collect()}
    assert result['unique'].run_id == plan.plan_id and result['unique'].match_status == 'matched'
    assert result['ambiguous'].candidate_run_count == 2 and result['ambiguous'].run_id is None
    assert result['ambiguous'].match_status == 'ambiguous'
    assert all(result[key].match_status == 'unmatched' and result[key].run_id is None
               for key in ['missing', 'foreign', 'wrong-notebook'])
    assert legacy.collect() == before


def test_historical_setup_probe_never_evaluates_rows(monkeypatch):
    """Repeated setup diagnostics preserve historical rows and table layout."""
    from importlib import import_module
    setup = import_module('fabricops_kit.config.setup_metadata_tables')
    calls = []

    class Historical:
        def collect(self):
            raise AssertionError('Historical rows must not be evaluated during setup')

    def read(name, **kwargs):
        calls.append((name, kwargs['schema']))
        return Historical()

    monkeypatch.setattr(setup, 'read_lakehouse_table', read)
    args = dict(config=SimpleNamespace(engineering_metadata_schema='engineering'), spark=object(), context={})
    for _ in range(2):
        warnings = setup._historical_table_warnings(**args)
        assert len(warnings) == 1 and 'never creates, updates or deletes' in warnings[0]
    assert calls == [('METADATA_DATA_LINEAGE', 'engineering')] * 2


def test_asset_usage_bounds_history_and_falls_back_to_run_time(runtime, spark_session, monkeypatch):
    """Old operations without timestamps select the newest Run before collection."""
    from fabricops_kit.data_contract import shared as contracts

    make, operation, *_ = runtime
    plan = make(mode='ungoverned', roles=('source',))
    operation(plan, 0)
    old = shared.pipeline_run_row(plan, status='incomplete')
    old.update(run_id='z-old', started_at=datetime(2020, 1, 1))
    old['operations'][0].update(started_at=None, completed_at=None)
    new = deepcopy(old)
    new.update(run_id='a-new', started_at=datetime(2026, 11, 20))
    runs = _frame(spark_session, [old, new])
    monkeypatch.setattr(contracts, 'read_lakehouse_table', lambda *a, **kw: runs)
    monkeypatch.setattr(contracts, '_metadata_io_context', lambda *a: {})
    rows = contracts.get_asset_pipeline_participation(config={}, routing_workspace_id='canary',
        spark_session=spark_session, table_id='table0')
    assert len(rows) == 1 and rows[0]['run_id'] == 'a-new'
    assert rows[0]['run_started_at'] == datetime(2026, 11, 20)


@pytest.mark.parametrize('timezone', ['UTC', 'Asia/Singapore'])
def test_latest_participation_treats_naive_operation_times_as_utc(runtime, spark_session, monkeypatch, timezone):
    """Historical naive timestamps and explicit offsets sort by the same instant."""
    from fabricops_kit.data_contract import shared as contracts

    make, operation, *_ = runtime
    plan = make(mode='ungoverned', roles=('source',))
    operation(plan, 0)
    latest = shared.pipeline_run_row(plan, status='incomplete')
    latest['run_id'] = 'latest-naive'
    latest['operations'][0].update(started_at='2026-11-20T01:00:00', completed_at=None)
    older = deepcopy(latest)
    older['run_id'] = 'older-aware'
    older['operations'][0]['started_at'] = '2026-11-20T00:30:00+00:00'
    runs = _frame(spark_session, [latest, older])
    monkeypatch.setattr(contracts, 'read_lakehouse_table', lambda *a, **kw: runs)
    monkeypatch.setattr(contracts, '_metadata_io_context', lambda *a: {})
    previous = spark_session.conf.get('spark.sql.session.timeZone')
    try:
        spark_session.conf.set('spark.sql.session.timeZone', timezone)
        rows = contracts.get_asset_pipeline_participation(config={}, routing_workspace_id='canary',
            spark_session=spark_session, table_id='table0')
        assert len(rows) == 1 and rows[0]['run_id'] == 'latest-naive'
    finally:
        spark_session.conf.set('spark.sql.session.timeZone', previous)
