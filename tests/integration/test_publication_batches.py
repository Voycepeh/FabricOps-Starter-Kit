"""Persisted Delta regressions for a reused interactive notebook activity.

Run with Delta Spark extensions enabled (the same atomic writer/merge semantics
used in Fabric); routing and metadata transport are isolated from Fabric APIs.
"""
# ruff: noqa: D102, D103, D107
from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace
from uuid import uuid4

import pytest

from fabricops_kit.pipeline import shared

writer = import_module("fabricops_kit.pipeline.pipeline_write")
io = import_module("fabricops_kit.io")

pytestmark = pytest.mark.spark


@pytest.fixture
def publication_runtime(monkeypatch, spark_session, tmp_path):
    DeltaTable = pytest.importorskip('delta.tables').DeltaTable

    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions')
    spark_session.conf.set('spark.databricks.delta.snapshotPartitions', '2')
    history = []
    state = {"activity": "interactive", "fail": None, "target": "target", "mode": "append"}
    context = {"config": object(), "env": "dev", "execution_plan": SimpleNamespace(permits_persistence=True, simulations=[])}

    def identity(*_args, **kwargs):
        name = kwargs.get("table_name", state["target"])
        return {"table_id": name, "table_name": name, "store": "Silver", "store_type": "lakehouse", "store_kind": "lakehouse", "schema": None}

    def read(name, **_kwargs):
        if name == "METADATA_SOURCE_OBSERVATION":
            return list(history)
        return spark_session.read.format('delta').load(str(tmp_path / name))

    def write(df, name, *, mode, **_kwargs):
        if state["fail"] == "before":
            raise RuntimeError('before physical write')
        if state["fail"] == "silent-skip":
            return
        df.write.format('delta').mode(mode).options(**(_kwargs.get('options') or {})).save(str(tmp_path / name))

    def merge_metadata(records, **_kwargs):
        if state["fail"] == "finalize" and any(r['observation_status'] == 'committed' for r in records):
            raise RuntimeError('metadata finalization interrupted')
        if not getattr(shared, 'persistence_permitted', lambda _: True)(context):
            return
        for record in records:
            key = tuple(record.get(k) for k in ('observation_id', 'partition_value', 'observation_status', 'target_table_id'))
            history[:] = [r for r in history if tuple(r.get(k) for k in ('observation_id', 'partition_value', 'observation_status', 'target_table_id')) != key]
            history.append(dict(record))

    def audit(**_kwargs):
        return dict(_committed_at=datetime.now(UTC), _committed_by='tester', _activity_id=state['activity'],
                    _workspace_id='workspace', _workspace_name='workspace', _notebook_id='notebook',
                    _notebook_name='02_pipeline', _metadata_lakehouse_name='Metadata')

    for module in (shared, writer):
        monkeypatch.setattr(module, 'resolve_fabric_context', lambda **kw: (context['config'], 'dev', context))
        monkeypatch.setattr(module, 'resolve_catalogue_table_identity', identity)
    monkeypatch.setattr(writer, 'resolve_physical_table_identity', identity)
    monkeypatch.setattr(shared, '_validated_observation_identity', lambda _c, _e, _t, ident: ident)
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', audit)
    monkeypatch.setattr(shared, 'get_spark_session', lambda: spark_session)
    monkeypatch.setattr(writer, 'resolve_target_audit_fields', lambda _c: audit())
    monkeypatch.setattr(writer, 'resolve_table_processing_definition', lambda *a, **k: (
        state['processing'] if state.get('processing') else {'load_strategy': state['mode']} if state['mode'] == 'append' else
        {'load_strategy': state['mode'], 'key_columns': ['id'], **({'effective_column': 'modified', 'tracked_columns': ['value']} if state['mode'] == 'scd2' else {})}))
    monkeypatch.setattr(writer, '_writer_scheduled_refresh', lambda **kw: {'status': 'not_configured', 'schedules': []})
    monkeypatch.setattr(writer, '_persist_target_processing', lambda **kw: None)
    monkeypatch.setattr(shared, 'persist_lineage_participation', lambda **kw: None)
    monkeypatch.setattr(shared, '_merge_source_observation_records', merge_metadata)
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *a: None)
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda store, name, schema, **kw: (store, name, schema, str(tmp_path / name)))
    monkeypatch.setattr(shared, 'read_lakehouse_table', read)
    monkeypatch.setattr(io, 'read_lakehouse_table', read)
    monkeypatch.setattr(io, 'write_lakehouse_table', write)
    monkeypatch.setattr(shared, 'write_lakehouse_table', write)
    for mapping in (shared._PENDING_SOURCE_OBSERVATIONS, shared._PENDING_SOURCE_DRIFT_OBSERVATIONS,
                    shared._INCREMENTAL_SOURCE_SCOPES, shared._CURRENT_TABLE_IDENTITIES):
        mapping.clear()
    shared._CURRENT_TABLE_IDENTITIES.update(source={'table_name': 'source'}, target=identity())

    def stage(day, *, incremental=True):
        rows = [(i, 'updated' if day >= 2 and i == 2 else 'initial', day if i == 2 else 1)
                for i in range(1, (9 if day == 1 else 13))]
        if state['mode'] != 'append':
            rows = [(i, 'price' if day >= 2 and i == 2 else 'category' if day >= 3 and i == 1 else 'initial',
                     2 if day >= 2 and i == 2 else 3 if day >= 3 and i == 1 else 1) for i in range(1, 9)]
        # Stage a physical Bronze snapshot separately from reading and merging.
        spark_session.createDataFrame(rows, 'id long, value string, modified long').write.format('delta').mode('overwrite').save(str(tmp_path / 'source'))
        df = read('source')
        if incremental:
            maximum = 8 if day == 1 else 12
            observation = [{'observation_id': str(uuid4()), 'source_table_id': 'source', 'target_table_id': '',
                            'environment_name': 'dev', 'partition_value': '', 'row_count': len(rows),
                            'min_change_value': '1', 'max_change_value': str(maximum), 'is_present': True,
                            'partition_column': 'id', 'change_column': 'id', **audit()}]
            scope = shared.resolve_incremental_source_scope(source_table_id='source', target_table_id=state['target'], observation=observation)
            if not scope['first_run']:
                df = df.where(df.id > int(scope['after']))
        return df

    def publish(df):
        return writer.pipeline_write(df, store='Silver', table_name=state['target'], source_table_ids=['source'], verbose=False)

    return SimpleNamespace(stage=stage, publish=publish, read=read, history=history, state=state, context=context,
                           spark=spark_session, path=tmp_path, delta=DeltaTable)


def test_three_day_incremental_append_and_same_batch_retry(publication_runtime):
    run = publication_runtime
    day1 = run.stage(1)
    run.publish(day1)
    day2 = run.stage(2)
    run.publish(day2)
    assert sorted(r.id for r in run.read('target').collect()) == list(range(1, 13))
    run.publish(day2)  # exact prepared batch, after metadata has finalized
    run.publish(run.stage(2))
    run.publish(run.stage(3))
    run.publish(run.stage(3))
    assert run.read('target').count() == 12


@pytest.mark.parametrize('mode', ['scd1', 'scd2'])
def test_three_day_scd_and_unchanged_retries(publication_runtime, mode):
    run = publication_runtime
    run.state['mode'] = mode
    for day, expected in [(1, 8), (2, 9), (3, 10)]:
        df = run.stage(day, incremental=False)
        assert df.where("id = 2 AND value = 'price'").count() == (0 if day == 1 else 1)
        run.publish(df)
        run.publish(df)
        persisted = run.read('target')
        assert persisted.count() == (8 if mode == 'scd1' else expected)
        current = persisted if mode == 'scd1' else persisted.where('_is_current')
        assert current.count() == 8
        assert current.where("id = 2 AND value = 'price'").count() == (0 if day == 1 else 1)
    run.state['activity'] = 'scheduled'
    run.publish(run.stage(3, incremental=False))
    assert run.read('target').count() == (8 if mode == 'scd1' else 10)


@pytest.mark.parametrize('failure', ['before', 'finalize'])
def test_interruption_and_cross_activity_recovery(publication_runtime, failure):
    run = publication_runtime
    run.publish(run.stage(1))
    run.state['fail'] = failure
    with pytest.raises(RuntimeError):
        run.publish(run.stage(2))
    assert run.read('target').count() == (8 if failure == 'before' else 12)
    assert not any(r['max_change_value'] == '12' and r['observation_status'] == 'committed' for r in run.history)
    run.state.update(fail=None, activity='next-activity')
    run.publish(run.stage(3))
    assert sorted(r.id for r in run.read('target').collect()) == list(range(1, 13))
    assert any(r['max_change_value'] == '12' and r['observation_status'] == 'committed' for r in run.history)


def test_testing_does_not_write_or_commit(publication_runtime):
    run = publication_runtime
    run.context['execution_plan'].permits_persistence = False
    result = run.publish(run.stage(1))
    assert result['published'] is False
    assert not run.delta.isDeltaTable(run.spark, str(run.path / 'target'))
    assert run.history == []


def test_checkpoint_isolation_across_physical_targets(publication_runtime):
    run = publication_runtime
    run.publish(run.stage(1))
    run.publish(run.stage(2))
    run.state['target'] = 'second_target'
    second = run.stage(3)
    assert second.count() == 12  # no baseline inherited from the first target
    run.publish(second)
    assert run.read('second_target').count() == 12
    assert run.read('target').count() == 12


def test_full_append_exact_retry_survives_new_activity(publication_runtime):
    run = publication_runtime
    df = run.stage(1, incremental=False)
    run.publish(df)
    run.state['activity'] = 'new-scheduled-activity'
    result = run.publish(df.orderBy('id', ascending=False))
    assert result['publication_status'] == 'already_applied'
    assert run.read('target').count() == 8


def test_existing_divergence_requires_explicit_verified_repair(publication_runtime):
    run = publication_runtime
    run.publish(run.stage(1))
    # Reproduce historical corruption: checkpoint claims Day 2 was accepted,
    # but the physical target still contains only Day 1.
    prior = next(r for r in run.history if r['observation_status'] == 'committed')
    run.history.append({**prior, 'observation_id': 'legacy-corruption', 'max_change_value': '12',
                        '_committed_at': datetime.now(UTC), 'publication_payload_json': None})
    result = run.publish(run.stage(3))
    assert result['publication_status'] == 'empty_incremental_scope'
    assert run.read('target').count() == 8  # never silently rewind or overwrite
    run.state['activity'] = 'explicit-reconciliation'
    source = run.stage(3, incremental=False)
    # The movement scenario is immutable by key. This controlled repair is
    # valid only after proving that the target is a matching subset.
    columns = ['id', 'value', 'modified']
    target = run.read('target').select(*columns)
    # This fixture changes i=2 in the later source; retain the accepted Day 1
    # value so that this test models immutable inventory movements.
    from pyspark.sql import functions as F
    source = source.withColumn('value', F.lit('initial')).withColumn('modified', F.lit(1).cast('long'))
    assert target.exceptAll(source.select(*columns)).count() == 0
    missing = source.join(target.select('id'), 'id', 'left_anti').select(*columns)
    assert missing.count() == 4
    before = list(run.history)
    run.publish(missing)
    assert run.read('target').select(*columns).exceptAll(source.select(*columns)).count() == 0
    assert source.select(*columns).exceptAll(run.read('target').select(*columns)).count() == 0
    assert len(run.history) == len(before)  # existing watermark not rewritten


@pytest.mark.parametrize('mode', ['scd1', 'scd2'])
def test_02c_product_master_snapshots_through_full_read(publication_runtime, monkeypatch, mode):
    """Exercise the actual Guided Demo inputs, Full Read and keyed SCD writes."""
    from pathlib import Path
    from pyspark.sql import functions as F
    reader = import_module('fabricops_kit.pipeline.pipeline_read')
    run = publication_runtime
    run.state['mode'] = mode
    run.state['processing'] = {'load_strategy': mode, 'key_columns': ['product_id']}
    if mode == 'scd2':
        run.state['processing'].update(effective_column='modified_datetime', tracked_columns=['product_name', 'product_category', 'list_price'])
    monkeypatch.setattr(reader, 'resolve_fabric_context', lambda: (run.context['config'], 'dev', run.context))
    monkeypatch.setattr(reader, 'resolve_catalogue_table_identity', lambda *a, **kw: {
        'table_id': 'source', 'table_name': 'source', 'store': 'Bronze', 'store_type': 'lakehouse', 'schema': None})
    monkeypatch.setattr(reader, 'resolve_pipeline_data_contract', lambda *a, **kw: None)
    monkeypatch.setattr(reader, 'read_lakehouse_table', run.read)
    assets = Path(__file__).resolve().parents[2] / 'templates' / 'DemoData'
    for day, versions in [(1, 8), (2, 9), (3, 10)]:
        staged = run.spark.read.option('header', True).option('inferSchema', True).csv(str(assets / f'products_day{day}.csv'))
        staged = staged.withColumn('list_price', F.col('list_price').cast('double')).withColumn('modified_datetime', F.to_timestamp('modified_datetime'))
        staged.write.format('delta').mode('overwrite').save(str(run.path / 'source'))
        source = reader.pipeline_read(table_id='source', read_mode='full', verbose=False)['dataframe']
        assert source.count() == 8
        expected_price = '39.90' if day == 1 else '44.90'
        assert source.where("product_id = 'P002'").first().list_price == pytest.approx(float(expected_price))
        prepared = source.select('product_id', 'product_name', 'product_category',
                                 F.col('list_price').cast('double').alias('list_price'),
                                 F.col('modified_datetime').cast('timestamp').alias('modified_datetime'))
        run.publish(prepared)
        run.publish(prepared)  # no duplicate history from unchanged inputs
        persisted = run.read('target')
        assert persisted.count() == (8 if mode == 'scd1' else versions)
        current = persisted if mode == 'scd1' else persisted.where('_is_current')
        assert current.select('product_id').distinct().count() == 8
        assert current.where("product_id = 'P002'").first().list_price == pytest.approx(float(expected_price))
        assert current.where("product_id = 'P001'").first().product_category == ('Travel Accessories' if day == 3 else 'Accessories')
        if mode == 'scd2':
            assert persisted.where('NOT _is_current AND _effective_to IS NULL').count() == 0
            assert persisted.groupBy('product_id', '_effective_from').count().where('count > 1').count() == 0


def test_exact_batch_retry_finalizes_after_physical_success(publication_runtime):
    run = publication_runtime
    run.publish(run.stage(1))
    day2 = run.stage(2)
    run.state['fail'] = 'finalize'
    with pytest.raises(RuntimeError, match='metadata finalization'):
        run.publish(day2)
    assert run.read('target').count() == 12
    run.state['fail'] = None
    retried = run.publish(day2)
    assert retried['publication_status'] == 'metadata_recovered'
    assert retried['write_metrics']['rows_committed'] == 0
    assert run.read('target').count() == 12
    assert any(r['max_change_value'] == '12' and r['observation_status'] == 'committed' for r in run.history)


def test_silent_physical_skip_cannot_advance_checkpoint(publication_runtime):
    """Even a successful writer return is insufficient without this batch's commit."""
    run = publication_runtime
    run.publish(run.stage(1))
    run.state['fail'] = 'silent-skip'
    with pytest.raises(RuntimeError, match='exact batch receipt'):
        run.publish(run.stage(2))
    assert run.read('target').count() == 8
    assert not any(r['max_change_value'] == '12' and r['observation_status'] == 'committed' for r in run.history)
    run.state.update(fail=None, activity='recovery')
    run.publish(run.stage(3))
    assert run.read('target').count() == 12


def test_concurrent_exact_append_accepts_only_winning_transaction(publication_runtime, monkeypatch):
    """Delta's batch transaction identity suppresses a competing identical write."""
    import json
    from pyspark.sql import functions as F
    run = publication_runtime
    run.publish(run.stage(1))
    day2 = run.stage(2)
    write = io.write_lakehouse_table

    def competing_write(df, name, **kwargs):
        attempted = dict(kwargs['options'])
        winner = json.loads(attempted['userMetadata'])
        winner.update(activity_id='competing-retry', committed_at=datetime.now(UTC).isoformat())
        competing = df.withColumn('_activity_id', F.lit(winner['activity_id'])).withColumn('_committed_at', F.lit(datetime.fromisoformat(winner['committed_at'])))
        write(competing, name, **{**kwargs, 'options': {**attempted, 'userMetadata': json.dumps(winner, sort_keys=True)}})
        # Same txnAppId/version: this physical attempt is atomically skipped.
        write(df, name, **kwargs)

    monkeypatch.setattr(io, 'write_lakehouse_table', competing_write)
    result = run.publish(day2)
    assert result['publication_status'] == 'already_applied'
    assert result['write_metrics']['rows_committed'] == 0
    assert sorted(r.id for r in run.read('target').collect()) == list(range(1, 13))
    accepted = [r for r in run.history if r['observation_status'] == 'committed' and r['max_change_value'] == '12']
    assert accepted and json.loads(accepted[0]['publication_payload_json'])['activity_id'] == 'competing-retry'


def test_later_read_cannot_finalize_an_older_publication(publication_runtime, monkeypatch):
    """A read between physical completion and finalization keeps its own checkpoint."""
    run = publication_runtime
    write = io.write_lakehouse_table
    next_read = {}

    def write_then_read(df, name, **kwargs):
        write(df, name, **kwargs)
        if not next_read:
            next_read['dataframe'] = run.stage(2)

    monkeypatch.setattr(io, 'write_lakehouse_table', write_then_read)
    run.publish(run.stage(1))
    assert run.read('target').count() == 8
    assert not any(r['max_change_value'] == '12' and r['observation_status'] == 'committed' for r in run.history)
    run.publish(next_read['dataframe'])
    assert sorted(r.id for r in run.read('target').collect()) == list(range(1, 13))


def test_02b_inventory_snapshots_through_incremental_read(publication_runtime, monkeypatch):
    """Use the actual inventory CSVs, bounded timestamp Read and demo Transform."""
    from pathlib import Path
    from pyspark.sql import functions as F
    reader = import_module('fabricops_kit.pipeline.pipeline_read')
    run = publication_runtime
    previous_zone = run.spark.conf.get('spark.sql.session.timeZone')
    run.spark.conf.set('spark.sql.session.timeZone', 'Asia/Singapore')
    identity = {'table_id': 'source', 'table_name': 'source', 'store': 'Bronze',
                'store_type': 'lakehouse', 'schema': None, 'load_strategy': 'append',
                'load_strategy_parameters_json': '{"watermark_column":"modified_datetime"}'}
    monkeypatch.setattr(reader, 'resolve_fabric_context', lambda: (run.context['config'], 'dev', run.context))
    monkeypatch.setattr(reader, 'resolve_catalogue_table_identity', lambda *a, **kw: identity)
    monkeypatch.setattr(reader, 'resolve_pipeline_data_contract', lambda *a, **kw: None)
    monkeypatch.setattr(reader, 'read_lakehouse_table', run.read)

    def capture(*, dataframe, **_kwargs):
        audit = writer.resolve_target_audit_fields(run.context)
        return [{**row, **audit, 'observation_id': str(uuid4()), 'environment_name': 'dev',
                 'source_table_id': 'source', 'target_table_id': '',
                 'partition_column': 'modified_datetime', 'change_column': 'modified_datetime'}
                for row in shared._observe_dataframe(dataframe, 'modified_datetime', 'modified_datetime', watermark_only=True)]

    monkeypatch.setattr(reader, 'capture_source_observation', capture)
    assets = Path(__file__).resolve().parents[2] / 'templates' / 'DemoData'
    try:
        for day, batch_rows, target_rows in [(1, 8, 8), (2, 4, 12), (2, 0, 12), (3, 0, 12), (3, 0, 12)]:
            if day in {1, 2}:
                incoming = run.spark.read.option('header', True).option('inferSchema', True).csv(str(assets / f'inventory_day{day}.csv'))
                staged = incoming if day == 1 else run.read('source').unionByName(incoming).dropDuplicates(['movement_id'])
                staged.write.format('delta').mode('overwrite').save(str(run.path / 'source'))
            source = reader.pipeline_read(table_id='source', read_mode='incremental', target_table_id='target', verbose=False)
            assert source['dataframe'].count() == batch_rows
            if day >= 2:
                assert source['scope']['through'] == '2026-10-07T02:30:00.000000Z'
            prepared = (source['dataframe'].withColumn('movement_date', F.to_date('modified_datetime'))
                        .withColumn('quantity_in', F.greatest(F.col('quantity_change'), F.lit(0)))
                        .withColumn('quantity_out', F.greatest(-F.col('quantity_change'), F.lit(0))))
            result = run.publish(prepared)
            assert run.read('target').count() == target_rows
            if batch_rows == 0:
                assert result['publication_status'] == 'empty_incremental_scope'
                assert not result['published']
        persisted = run.read('target')
        assert sorted(row.movement_id for row in persisted.select('movement_id').collect()) == [f'M{i:03}' for i in range(1, 13)]
        assert persisted.select('_activity_id').distinct().count() == 1
    finally:
        run.spark.conf.set('spark.sql.session.timeZone', previous_zone)
