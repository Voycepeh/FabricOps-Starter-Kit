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
    merge_processing_state = shared._merge_source_observation_records
    history = []
    state = {"activity": "interactive", "fail": None, "target": "target", "mode": "append"}
    context = {"config": object(), "env": "dev", "execution_plan": SimpleNamespace(permits_persistence=True, simulations=[])}

    def identity(*_args, **kwargs):
        name = kwargs.get("table_name", state["target"])
        return {"table_id": name, "table_name": name, "store": "Silver", "store_type": "lakehouse", "store_kind": "lakehouse", "schema": None}

    def read(name, **_kwargs):
        if name == "METADATA_PROCESSING_STATE":
            if state.get("durable_metadata"):
                return spark_session.read.format("delta").load(str(tmp_path / name))
            return list(history)
        return spark_session.read.format('delta').load(str(tmp_path / name))

    def write(df, name, *, mode, **_kwargs):
        if state["fail"] == "before":
            raise RuntimeError('before physical write')
        if state["fail"] == "silent-skip":
            return
        df.write.format('delta').mode(mode).options(**(_kwargs.get('options') or {})).save(str(tmp_path / name))

    def merge_metadata(records, **_kwargs):
        if state["fail"] == "finalize" and any(r['status'] == 'committed' for r in records):
            raise RuntimeError('metadata finalization interrupted')
        if not getattr(shared, 'persistence_permitted', lambda _: True)(context):
            return
        if state.get("durable_metadata"):
            merge_processing_state(records, config=context["config"], context=context)
            history[:] = shared.observation_rows(read("METADATA_PROCESSING_STATE"))
            return
        for record in records:
            key = tuple(record.get(k) for k in ('record_id',))
            history[:] = [r for r in history if tuple(r.get(k) for k in ('record_id',)) != key]
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
    monkeypatch.setattr(shared, 'get_spark_session', lambda *_args, **_kwargs: spark_session)
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
                    shared._INCREMENTAL_SOURCE_SCOPES, shared._ACTIVE_PUBLICATION_SOURCES, shared._CURRENT_TABLE_IDENTITIES):
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
                            'partition_column': 'id', 'change_column': 'id', 'watermark_type': 'bigint', **audit()}]
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
    assert not any(r.get('max_change_value') == '12' and r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' for r in run.history)
    run.state.update(fail=None, activity='next-activity')
    run.publish(run.stage(3))
    assert sorted(r.id for r in run.read('target').collect()) == list(range(1, 13))
    assert any(r.get('max_change_value') == '12' and r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' for r in run.history)


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
    prior = next(r for r in run.history if r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed')
    run.history.append({**prior, 'observation_id': 'legacy-corruption', 'max_change_value': '12',
                        '_committed_at': datetime.now(UTC), 'publication_id': None, 'record_id': 'reconciled-checkpoint'})
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
    assert [row for row in run.history if row["record_type"] == "incremental_checkpoint"] == [row for row in before if row["record_type"] == "incremental_checkpoint"]
    assert len(run.history) == len(before) + 1  # repair adds only its target publication receipt


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
    assert any(r.get('max_change_value') == '12' and r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' for r in run.history)


def test_silent_physical_skip_cannot_advance_checkpoint(publication_runtime):
    """Even a successful writer return is insufficient without this batch's commit."""
    run = publication_runtime
    run.publish(run.stage(1))
    run.state['fail'] = 'silent-skip'
    with pytest.raises(RuntimeError, match='exact batch receipt'):
        run.publish(run.stage(2))
    assert run.read('target').count() == 8
    assert not any(r.get('max_change_value') == '12' and r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' for r in run.history)
    run.state.update(fail=None, activity='recovery')
    run.publish(run.stage(3))
    assert run.read('target').count() == 12


@pytest.mark.parametrize("durable_winner", [False, True])
def test_concurrent_exact_append_accepts_only_winning_transaction(publication_runtime, monkeypatch, request, durable_winner):
    """Delta's batch transaction identity suppresses a competing identical write."""
    import json
    from pyspark.sql import functions as F
    run = publication_runtime
    if durable_winner:
        request.getfixturevalue("durable_processing_state")
    run.publish(run.stage(1))
    day2 = run.stage(2)
    write = io.write_lakehouse_table

    def competing_write(df, name, **kwargs):
        attempted = dict(kwargs['options'])
        winner = json.loads(attempted['userMetadata'])
        winner.update(activity_id='competing-retry', committed_at=datetime.now(UTC).isoformat())
        if durable_winner:
            winner["run_id"] = "competing-run"
            origin = shared.source_observation_run_id(run.context) or run.state["activity"]
            snapshot = shared.snapshot_pipeline_write_observations(environment_name="dev", activity_id=origin,
                target_table_id="target", source_table_ids=["source"])
            winner_context = {**run.context, "execution_plan": SimpleNamespace(permits_persistence=True, plan_id="competing-run")}
            staged = shared._pipeline_write_state_records({"target_table_id": "target", "source_table_ids": ["source"],
                "publication": winner, "observation_snapshot": snapshot, "context": winner_context},
                audit={**writer.resolve_target_audit_fields(run.context), "_activity_id": winner["activity_id"]}, env="dev", status="staged")
            shared._merge_source_observation_records(staged, config=run.context["config"], context=run.context)
        competing = df.withColumn('_activity_id', F.lit(winner['activity_id'])).withColumn('_committed_at', F.lit(datetime.fromisoformat(winner['committed_at'])))
        write(competing, name, **{**kwargs, 'options': {**attempted, 'userMetadata': json.dumps(winner, sort_keys=True)}})
        # Same txnAppId/version: this physical attempt is atomically skipped.
        write(df, name, **kwargs)

    monkeypatch.setattr(io, 'write_lakehouse_table', competing_write)
    result = run.publish(day2)
    assert result['publication_status'] == ('metadata_recovered' if durable_winner else 'already_applied')
    assert result['write_metrics']['rows_committed'] == 0
    assert sorted(r.id for r in run.read('target').collect()) == list(range(1, 13))
    accepted = [r for r in run.history if r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' and r.get('max_change_value') == '12']
    assert accepted and shared._publication_receipt(accepted[0], run.history)['activity_id'] == 'competing-retry'
    if durable_winner:
        assert {row["run_id"] for row in accepted} == {"competing-run"}
        members = [row for row in run.history if row.get("publication_id") == accepted[0]["publication_id"]]
        assert {row["status"] for row in members} == {"committed"}


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
    assert not any(r.get('max_change_value') == '12' and r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' for r in run.history)
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
                'load_strategy_parameters_json': {'watermark_column': 'modified_datetime'}}
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



def test_scd1_recurring_snapshot_after_partial_publication(publication_runtime):
    """A surviving old row marker must not suppress a newly requested snapshot."""
    run = publication_runtime
    run.state['mode'] = 'scd1'
    original = run.spark.createDataFrame([(1, 'A', 1), (2, 'A', 1)], 'id long, value string, modified long')
    run.publish(original)
    run.publish(run.spark.createDataFrame([(1, 'B', 2)], original.schema))
    run.state['activity'] = 'new-scheduled-activity'
    result = run.publish(original)
    assert result['publication_status'] == 'published'
    assert sorted((row.id, row.value) for row in run.read('target').collect()) == [(1, 'A'), (2, 'A')]
    assert run.publish(original)['publication_status'] == 'already_applied'


def test_newer_read_cannot_replace_an_unpublished_checkpoint(publication_runtime):
    """Reject ambiguous Reads before they can pair newer progress with old rows."""
    run = publication_runtime
    run.publish(run.stage(1))
    earlier = run.stage(2).where('id <= 12').cache()
    try:
        assert earlier.count() == 4
        key = ('dev', 'interactive', 'source', 'target')
        newer = [{**shared._PENDING_SOURCE_OBSERVATIONS[key][0], 'observation_id': str(uuid4()),
                  'row_count': 16, 'max_change_value': '16', '_committed_at': datetime.now(UTC)}]
        source = run.read('source').unionByName(run.spark.createDataFrame(
            [(i, 'initial', 1) for i in range(13, 17)], earlier.schema))
        source.write.format('delta').mode('overwrite').save(str(run.path / 'source'))
        with pytest.raises(RuntimeError, match='already awaiting publication'):
            shared.resolve_incremental_source_scope(source_table_id='source', target_table_id='target', observation=newer)
        run.publish(earlier)
        assert run.read('target').count() == 12
        assert not any(r.get('max_change_value') == '16' and r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' for r in run.history)
        scope = shared.resolve_incremental_source_scope(source_table_id='source', target_table_id='target', observation=newer)
        assert scope['after'] == '12'
        run.publish(run.read('source').where('id > 12 AND id <= 16'))
        assert sorted(row.id for row in run.read('target').collect()) == list(range(1, 17))
    finally:
        earlier.unpersist()


@pytest.fixture
def warehouse_publication_runtime(publication_runtime, monkeypatch):
    """Mock Warehouse transport while persisting all target rows in real Delta."""
    import re
    from pyspark.sql import functions as F
    run = publication_runtime
    monkeypatch.setattr(writer, 'resolve_physical_table_identity', lambda *a, **kw: {
        'table_id': 'target', 'table_name': 'target', 'store': 'Silver',
        'store_type': 'warehouse', 'store_kind': 'warehouse', 'schema': 'dbo'})

    def warehouse_write(df, schema, table_name, *, mode, **kw):
        if run.state['fail'] == 'before':
            raise RuntimeError('before physical write')
        df.write.format('delta').mode(mode).save(str(run.path / table_name))

    def warehouse_query(sql, **kw):
        target = run.read('target')
        if 'MAX([_committed_at])' in sql:
            return target.agg(F.max('_committed_at').alias('fabricops_latest_publication'))
        activity = re.search(r"\[_activity_id\] = '([^']+)'", sql).group(1)
        stamp = datetime.fromisoformat(re.search(r"CAST\('([^']+)' AS", sql).group(1)).replace(tzinfo=UTC)
        return target.where((F.col('_activity_id') == activity) & (F.col('_committed_at') == F.lit(stamp))).agg(F.count('*').alias('fabricops_publication_rows'))

    monkeypatch.setattr(io, 'write_warehouse_table', warehouse_write)
    monkeypatch.setattr(shared, 'read_warehouse_query', warehouse_query)
    return run


@pytest.mark.parametrize('source_free', [False, True])
@pytest.mark.parametrize('failure', [None, 'before', 'finalize'])
def test_warehouse_full_append_has_durable_retry_receipt(warehouse_publication_runtime, source_free, failure):
    run = warehouse_publication_runtime
    df = run.stage(1, incremental=False)
    def publish():
        return writer.pipeline_write(df, store='Silver', table_name='target',
                                     source_table_ids=[] if source_free else ['source'], verbose=False)
    run.state['fail'] = failure
    if failure:
        with pytest.raises(RuntimeError):
            publish()
    else:
        publish()
    run.state.update(fail=None, activity='cross-activity-retry')
    result = publish()
    assert run.read('target').count() == 8
    assert result['publication_status'] == ('published' if failure == 'before' else 'metadata_recovered' if failure == 'finalize' else 'already_applied')
    assert any(row['record_type'] == 'publication_receipt' and row['status'] == 'committed' for row in run.history)
    assert not any(row['record_type'] == 'incremental_checkpoint' and row['status'] == 'committed' for row in run.history)
    publish()
    assert run.read('target').count() == 8


def test_retained_published_frame_cannot_accept_a_new_read_checkpoint(publication_runtime):
    """Reusing an old notebook variable must not turn its receipt into newer progress."""
    run = publication_runtime
    initial = run.stage(1)
    old = run.spark.createDataFrame(initial.collect(), initial.schema).cache()
    try:
        run.publish(old)
        next_batch = run.stage(2)
        with pytest.raises(RuntimeError, match='does not match this Read'):
            run.publish(old)
        assert run.read('target').count() == 8
        assert not any(r.get('max_change_value') == '12' and r['record_type'] == 'incremental_checkpoint' and r['status'] == 'committed' for r in run.history)
        run.publish(next_batch)
        assert run.read('target').count() == 12
    finally:
        old.unpersist()



@pytest.mark.parametrize('mode', ['scd1', 'scd2'])
def test_warehouse_scd_retry_requires_latest_publication(warehouse_publication_runtime, monkeypatch, mode):
    """Emulate Warehouse transactional merges and inspect their persisted rows."""
    run = warehouse_publication_runtime
    run.state['mode'] = mode
    warehouse_io = import_module('fabricops_kit.io.shared')
    def merge(df, *, schema, table_name, store, processing, context, options):
        shared.execute_lakehouse_processing(df, schema=schema, table_name=table_name, store=store,
                                           processing=processing, scope={'type': 'full_dataset'}, context=context)
    monkeypatch.setattr(warehouse_io, 'execute_warehouse_processing', merge)
    original = run.spark.createDataFrame([(1, 'A', 1), (2, 'A', 1)], 'id long, value string, modified long')
    run.publish(original)
    run.publish(run.spark.createDataFrame([(1, 'B', 2)], original.schema))
    run.state['activity'] = 'new-scheduled-activity'
    if mode == 'scd2':
        # A historical receipt must not conceal an invalid backwards update.
        with pytest.raises(ValueError, match='effective time later'):
            run.publish(original)
        current_input = run.spark.createDataFrame([(1, 'A', 3), (2, 'A', 1)], original.schema)
    else:
        current_input = original
    assert run.publish(current_input)['publication_status'] == 'published'
    assert run.publish(current_input)['publication_status'] == 'already_applied'
    target = run.read('target')
    assert target.count() == (2 if mode == 'scd1' else 4)
    current = target if mode == 'scd1' else target.where('_is_current')
    assert sorted((row.id, row.value) for row in current.collect()) == [(1, 'A'), (2, 'A')]


@pytest.mark.parametrize('mode', ['append', 'scd1', 'scd2'])
def test_distinct_runs_share_real_activity_and_isolate_source_state(publication_runtime, mode):
    run = publication_runtime
    run.state['mode'] = mode
    for day, expected in [(1, 8), (2, 9), (3, 10)]:
        run.context['execution_plan'].plan_id = f'pipeline-run-{day}'
        run.publish(run.stage(day, incremental=mode == 'append'))
        assert run.read('target').count() == (expected if mode == 'scd2' else 8 if mode == 'scd1' or day == 1 else 12)
    assert {row._activity_id for row in run.read('target').select('_activity_id').collect()} == {'interactive'}
    if mode == 'append':
        accepted = [row for row in run.history if row['record_type'] == 'incremental_checkpoint' and row['status'] == 'committed']
        assert {row['run_id'] for row in accepted} == {'pipeline-run-1', 'pipeline-run-2'}
        import json
        assert {shared._publication_receipt(row, run.history)['run_id'] for row in accepted} == {'pipeline-run-1', 'pipeline-run-2'}


def test_new_run_recovers_old_run_publication_without_duplicate_append(publication_runtime):
    run = publication_runtime
    run.context['execution_plan'].plan_id = 'original-run'
    run.publish(run.stage(1))
    run.state['fail'] = 'finalize'
    with pytest.raises(RuntimeError):
        run.publish(run.stage(2))
    assert run.read('target').count() == 12
    run.context['execution_plan'].plan_id = 'retry-run'
    run.state['fail'] = None
    result = run.publish(run.stage(3))
    assert result['publication_status'] == 'empty_incremental_scope'
    assert run.read('target').count() == 12
    accepted = [row for row in run.history if row['record_type'] == 'incremental_checkpoint' and row['status'] == 'committed' and row['max_change_value'] == '12']
    assert accepted and all(row['run_id'] == 'original-run' for row in accepted)


def test_new_run_exact_retry_can_finalize_at_same_checkpoint(publication_runtime):
    run = publication_runtime
    run.context['execution_plan'].plan_id = 'baseline-run'
    run.publish(run.stage(1))
    run.context['execution_plan'].plan_id = 'old-run'
    old_scope = run.stage(2)
    old = run.spark.createDataFrame(old_scope.collect(), old_scope.schema)
    run.context['execution_plan'].plan_id = 'new-run'
    run.publish(run.stage(2))
    assert run.read('target').count() == 12
    run.context['execution_plan'].plan_id = 'old-run'
    # The exact receipt proves these rows already arrived, so this is a safe
    # metadata-only retry at the same upper watermark, never another append.
    assert run.publish(old)['publication_status'] == 'already_applied'
    assert run.read('target').count() == 12


def test_retained_old_run_cannot_append_after_a_later_run_advances_checkpoint(publication_runtime):
    run = publication_runtime
    run.context['execution_plan'].plan_id = 'baseline-run'
    run.publish(run.stage(1))
    run.context['execution_plan'].plan_id = 'old-run'
    old_scope = run.stage(2)
    old = run.spark.createDataFrame(old_scope.collect(), old_scope.schema)
    prior = shared._PENDING_SOURCE_OBSERVATIONS[('dev', 'old-run', 'source', 'target')][0]
    run.context['execution_plan'].plan_id = 'new-run'
    newer = [{**prior, 'observation_id': str(uuid4()), 'row_count': 16, 'max_change_value': '16'}]
    shared.resolve_incremental_source_scope(source_table_id='source', target_table_id='target', observation=newer)
    extra = run.spark.createDataFrame([(i, 'initial', 1) for i in range(13, 17)], old.schema)
    run.publish(old.unionByName(extra))
    assert run.read('target').count() == 16
    run.context['execution_plan'].plan_id = 'old-run'
    with pytest.raises(RuntimeError, match='checkpoint advanced'):
        run.publish(old)
    assert run.read('target').count() == 16
    assert max(int(row['max_change_value']) for row in run.history if row['record_type'] == 'incremental_checkpoint' and row['status'] == 'committed') == 16


@pytest.fixture
def durable_processing_state(publication_runtime):
    """Exercise the real metadata Delta merge as well as persisted business rows."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    run = publication_runtime
    run.spark.createDataFrame([], metadata_table_schema_registry()["METADATA_PROCESSING_STATE"]).write.format("delta").save(
        str(run.path / "METADATA_PROCESSING_STATE"))
    run.state["durable_metadata"] = True
    return run


@pytest.mark.parametrize("failure", ["before", "finalize"])
def test_durable_checkpoint_recovery_preserves_exact_progress(durable_processing_state, failure):
    run = durable_processing_state
    run.context["execution_plan"].plan_id = "originating-run"
    run.publish(run.stage(1))
    run.state["fail"] = failure
    with pytest.raises(RuntimeError):
        run.publish(run.stage(2))
    checkpoints = run.read("METADATA_PROCESSING_STATE").where("record_type = 'incremental_checkpoint'")
    assert {row.max_change_value for row in checkpoints.where("status = 'committed'").collect()} == {"8"}
    assert checkpoints.where("status = 'staged' AND max_change_value = '12'").count() == 1
    run.context["execution_plan"].plan_id = "recovery-run"
    run.state["fail"] = None
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._INCREMENTAL_SOURCE_SCOPES.clear()
    run.publish(run.stage(2))
    assert sorted(row.id for row in run.read("target").collect()) == list(range(1, 13))
    accepted = run.read("METADATA_PROCESSING_STATE").where("record_type = 'incremental_checkpoint' AND status = 'committed'")
    assert {row.max_change_value for row in accepted.collect()} == {"8", "12"}
    assert "publication_payload_json" not in accepted.columns
    assert all(row.publication_id and row.accepted_at for row in accepted.collect())
    assert run.publish(run.stage(2))["publication_status"] == "empty_incremental_scope"
    assert run.read("target").count() == 12


def test_durable_multi_source_recovery_is_one_transaction(durable_processing_state):
    run = durable_processing_state
    run.context["execution_plan"].plan_id = "one-logical-run"
    frame = run.stage(1)
    key = ("dev", "one-logical-run", "source", "target")
    current = shared._PENDING_SOURCE_OBSERVATIONS[key]
    shared._PENDING_SOURCE_OBSERVATIONS[("dev", "one-logical-run", "other-source", "target")] = [
        {**row, "source_table_id": "other-source", "observation_id": "other-observation"} for row in current]
    shared._CURRENT_TABLE_IDENTITIES["other-source"] = {"table_name": "other_source"}
    shared._PENDING_SOURCE_DRIFT_OBSERVATIONS[key] = [{**row, "partition_value": "p1"} for row in current]
    run.state["fail"] = "finalize"
    with pytest.raises(RuntimeError, match="metadata finalization"):
        writer.pipeline_write(frame, store="Silver", table_name="target", source_table_ids=["source", "other-source"], verbose=False)
    before = run.delta.forPath(run.spark, str(run.path / "METADATA_PROCESSING_STATE")).history(1).first().version
    rows = shared.observation_rows(run.read("METADATA_PROCESSING_STATE"))
    assert {row["record_type"] for row in rows} == {"publication_receipt", "incremental_checkpoint", "drift_baseline"}
    assert {row["status"] for row in rows} == {"staged"}
    run.state["fail"] = None
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._PENDING_SOURCE_DRIFT_OBSERVATIONS.clear()
    run.context["execution_plan"].plan_id = "restarted-run"
    shared._recover_completed_source_observations(run.read("METADATA_PROCESSING_STATE"), config=run.context["config"], env="dev",
                                                context=run.context, source_table_id="source", target_table_id="target")
    table = run.delta.forPath(run.spark, str(run.path / "METADATA_PROCESSING_STATE"))
    assert table.history(1).first().version == before + 1
    accepted = shared.observation_rows(table.toDF())
    assert len(accepted) == 4
    assert {row["status"] for row in accepted} == {"committed"}
    assert {row["run_id"] for row in accepted} == {"one-logical-run"}
    assert len({row["accepted_at"] for row in accepted}) == 1
    assert len({row["publication_id"] for row in accepted}) == 1
    # A repeated stage cannot regress a durable acknowledgement.
    shared._merge_source_observation_records(rows, config=run.context["config"], context=run.context)
    assert {row.status for row in table.toDF().collect()} == {"committed"}


def test_partial_warehouse_append_is_never_accepted_or_republished(warehouse_publication_runtime, monkeypatch):
    run = warehouse_publication_runtime
    monkeypatch.setattr(writer, "_target_has_rows", lambda **kw: False)
    def partial_write(frame, schema, table_name, **kwargs):
        frame.limit(1).write.format("delta").mode("overwrite").save(str(run.path / table_name))
    monkeypatch.setattr(io, "write_warehouse_table", partial_write)
    frame = run.stage(1)
    with pytest.raises(RuntimeError, match="Incomplete Warehouse publication"):
        run.publish(frame)
    assert run.read("target").count() == 1
    assert {row["status"] for row in run.history} == {"staged"}
    monkeypatch.setattr(io, "write_warehouse_table", lambda *a, **kw: pytest.fail("partial append must require reconciliation"))
    with pytest.raises(RuntimeError, match="Incomplete Warehouse publication"):
        run.publish(frame)
    assert run.read("target").count() == 1



def test_captured_observation_is_typed_but_never_accepted_progress(durable_processing_state, monkeypatch):
    run = durable_processing_state
    frame = run.stage(1)
    monkeypatch.setattr(shared, "get_store", lambda *a, **kw: SimpleNamespace(schema_enabled=False))
    monkeypatch.setattr(shared, "resolve_lakehouse_table_location", lambda *a, **kw: ("source", None, "source-path"))
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *a, **kw: [])
    evidence = shared.capture_source_observation(table_id="source", dataframe=frame, incremental_columns=("id", "id"),
        source_identity={"table_id": "source", "store": "Bronze", "table_name": "source", "store_kind": "lakehouse"}, context=run.context)
    persisted = run.read("METADATA_PROCESSING_STATE")
    row = persisted.first()
    assert persisted.count() == 1
    assert row.record_type == "source_observation" and row.status == "observed"
    assert row.watermark_type == "bigint" and row.change_column == "id"
    assert row.max_change_value == "8" and row.row_count == 8
    assert row.observed_at and row.accepted_at is None and row.publication_id is None
    assert shared._latest_source_target_observation(persisted, source_table_id="source", target_table_id="target", environment_name="dev") == []
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._INCREMENTAL_SOURCE_SCOPES.clear()
    scope = shared.resolve_incremental_source_scope(source_table_id="source", target_table_id="target", observation=evidence, context=run.context)
    assert scope["first_run"]
    run.publish(frame)
    accepted = run.read("METADATA_PROCESSING_STATE")
    assert {r.record_type for r in accepted.collect()} == {"source_observation", "incremental_checkpoint", "publication_receipt"}
    assert shared._latest_source_target_observation(accepted, source_table_id="source", target_table_id="target", environment_name="prod") == []
    assert shared._latest_source_target_observation(accepted, source_table_id="other-source", target_table_id="target", environment_name="dev") == []
    checkpoint = shared._latest_source_target_observation(accepted, source_table_id="source", target_table_id="target", environment_name="dev")[0]
    assert checkpoint["watermark_type"] == "bigint" and checkpoint["max_change_value"] == "8"


@pytest.mark.parametrize("store_kind", ["lakehouse", "warehouse"])
def test_exact_retry_without_volatile_snapshots_accepts_all_original_members(durable_processing_state, request, monkeypatch, store_kind):
    """A restarted exact Write must acknowledge the durable batch, including every source."""
    run = durable_processing_state
    if store_kind == "warehouse":
        request.getfixturevalue("warehouse_publication_runtime")
        monkeypatch.setattr(writer, "_target_has_rows", lambda **kw: False)
        shared._CURRENT_TABLE_IDENTITIES["target"] = {
            "table_id": "target", "table_name": "target", "store": "Silver", "schema": "dbo", "store_type": "warehouse"}
    run.context["execution_plan"].plan_id = "original-run"
    frame = run.stage(1)
    key = ("dev", "original-run", "source", "target")
    original = shared._PENDING_SOURCE_OBSERVATIONS[key]
    shared._PENDING_SOURCE_OBSERVATIONS[("dev", "original-run", "other-source", "target")] = [
        {**row, "source_table_id": "other-source", "observation_id": "other-snapshot"} for row in original]
    shared._PENDING_SOURCE_DRIFT_OBSERVATIONS[key] = [{**row, "partition_value": "p1"} for row in original]
    shared._CURRENT_TABLE_IDENTITIES["other-source"] = {"table_name": "other_source"}

    def publish(dataframe):
        return writer.pipeline_write(dataframe, store="Silver", table_name="target", source_table_ids=["source", "other-source"], verbose=False)

    run.state["fail"] = "finalize"
    with pytest.raises(RuntimeError, match="metadata finalization"):
        publish(frame)
    staged = shared.observation_rows(run.read("METADATA_PROCESSING_STATE"))
    assert len(staged) == 4 and {row["status"] for row in staged} == {"staged"}
    run.state["fail"] = None
    run.context["execution_plan"].plan_id = "restarted-run"
    for cache in (shared._PENDING_SOURCE_OBSERVATIONS, shared._PENDING_SOURCE_DRIFT_OBSERVATIONS, shared._INCREMENTAL_SOURCE_SCOPES):
        cache.clear()
    writer_name = "write_warehouse_table" if store_kind == "warehouse" else "write_lakehouse_table"
    monkeypatch.setattr(io, writer_name, lambda *a, **kw: pytest.fail("an exact verified retry must not publish twice"))
    result = publish(run.read("source"))
    accepted = shared.observation_rows(run.read("METADATA_PROCESSING_STATE"))
    assert result["publication_status"] == "metadata_recovered"
    assert {row["record_id"] for row in accepted} == {row["record_id"] for row in staged}
    assert {row["status"] for row in accepted} == {"committed"}
    assert {row["run_id"] for row in accepted} == {"original-run"}
    assert len({row["accepted_at"] for row in accepted}) == 1
    for source_id in ("source", "other-source"):
        checkpoint = shared._latest_source_target_observation(accepted, source_table_id=source_id, target_table_id="target", environment_name="dev")
        assert len(checkpoint) == 1 and checkpoint[0]["max_change_value"] == "8"
    publish(run.read("source"))
    assert {row["record_id"]: row for row in shared.observation_rows(run.read("METADATA_PROCESSING_STATE"))} == {
        row["record_id"]: row for row in accepted}
    assert run.read("target").count() == 8


def test_recovery_includes_a_previously_acknowledged_receipt(durable_processing_state):
    """Repair a receipt-only acknowledgement without losing or rewriting its origin."""
    run = durable_processing_state
    frame = run.stage(1)
    run.state["fail"] = "finalize"
    with pytest.raises(RuntimeError, match="metadata finalization"):
        run.publish(frame)
    run.state["fail"] = None
    rows = shared.observation_rows(run.read("METADATA_PROCESSING_STATE"))
    receipt = next(row for row in rows if row["record_type"] == "publication_receipt")
    receipt = {**receipt, "status": "committed", "accepted_at": datetime.now(UTC)}
    shared._merge_source_observation_records([receipt], config=run.context["config"], context=run.context)
    table = run.delta.forPath(run.spark, str(run.path / "METADATA_PROCESSING_STATE"))
    receipt = next(row for row in shared.observation_rows(table.toDF()) if row["record_type"] == "publication_receipt")
    before = table.history(1).first().version
    recovered = shared._recover_completed_source_observations(table.toDF(), config=run.context["config"], env="dev",
        context=run.context, source_table_id="source", target_table_id="target")
    assert table.history(1).first().version == before + 1
    assert {row["status"] for row in recovered} == {"committed"}
    persisted = shared.observation_rows(run.read("METADATA_PROCESSING_STATE"))
    assert {row["status"] for row in persisted} == {"committed"}
    assert next(row for row in persisted if row["record_type"] == "publication_receipt") == receipt
    assert run.read("target").count() == 8


@pytest.mark.parametrize("partition_value", [None, "", [None, ""]])
def test_empty_drift_snapshot_has_unique_durable_partition_keys(durable_processing_state, monkeypatch, partition_value):
    """The empty-source row must not duplicate a null/empty partition tombstone."""
    import json
    run = durable_processing_state
    run.state["processing"] = {"load_strategy": "overwrite"}
    source_rule = {"table_id": "source", "environment_name": "dev", "guardrail_type": "source_drift", "rule_type": "historical_mutation",
                   "action": "Block", "is_active": True, "guardrail_rule_id": "source-drift",
                   "rule_parameters_json": json.dumps({"partition_column": "partition", "change_column": "modified"})}
    monkeypatch.setattr(shared, "get_store", lambda *a, **kw: SimpleNamespace(schema_enabled=False))
    monkeypatch.setattr(shared, "resolve_lakehouse_table_location", lambda *a, **kw: ("source", None, "source-path"))
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *a, **kw: [source_rule])
    monkeypatch.setattr(shared, "write_guardrail_result_row", lambda **kw: None)
    partitions = partition_value if isinstance(partition_value, list) else [partition_value]
    initial = run.spark.createDataFrame([(index, value, 1) for index, value in enumerate(partitions)], "id long, partition string, modified long")
    for frame in (initial, initial.limit(0), initial.limit(0)):
        shared.capture_source_observation(table_id="source", dataframe=frame, context=run.context,
            source_identity={"table_id": "source", "store": "Bronze", "table_name": "source", "store_kind": "lakehouse"})
        check = shared.check_source_drift_for_target(source_table_id="source", target_table_id="target",
            source_processing={"load_strategy": "overwrite"}, context=run.context)
        assert check["can_continue"]
        run.publish(frame)
        metadata = run.read("METADATA_PROCESSING_STATE")
        assert metadata.groupBy("record_id").count().where("count > 1").count() == 0
    assert run.read("target").count() == 0
    baseline = shared._previous_source_target_observation(run.read("METADATA_PROCESSING_STATE"), source_table_id="source",
        target_table_id="target", environment_name="dev", committed_at=datetime.now(UTC).replace(tzinfo=None))
    assert len(baseline) == len(partitions) + 1
    assert len([row for row in baseline if row["is_present"] is None]) == 1
    removed = [row for row in baseline if row["is_present"] is False]
    assert {row["partition_value"] for row in removed} == set(partitions)
