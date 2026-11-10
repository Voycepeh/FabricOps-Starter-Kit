"""Distributed exact hashes and multiplicities for pipeline-owned Source Drift."""
# ruff: noqa: D103
import pytest
from fabricops_kit.pipeline import shared


@pytest.mark.parametrize('keys,expected', [(['id'], (1, 1, 1)), ([], (2, None, 2))])
def test_added_removed_modified_are_only_paired_with_reliable_keys(spark_session, keys, expected):
    old = spark_session.createDataFrame([(1, 'a'), (2, 'b'), (3, 'c')], 'id int, value string')
    new = spark_session.createDataFrame([(1, 'a'), (2, 'changed'), (4, 'd')], old.schema)
    previous, _ = shared.source_snapshot_projection(old, keys)
    current, _ = shared.source_snapshot_projection(new, keys)
    result = shared.compare_source_snapshot_evidence(current, previous, keyed=bool(keys))
    assert (result['added_count'], result['modified_count'], result['removed_count']) == expected
    assert all(len(rows) <= 10 for rows in result['samples'].values())
    assert 'value' not in str(result['samples'])


def test_duplicate_multiplicities_are_preserved_without_arbitrary_pairing(spark_session):
    old = spark_session.createDataFrame([(1, 'a'), (1, 'a'), (2, 'b')], 'id int, value string')
    new = spark_session.createDataFrame([(1, 'a'), (2, 'b'), (2, 'b'), (3, 'c')], old.schema)
    previous, old_meta = shared.source_snapshot_projection(old, ['id'])
    current, new_meta = shared.source_snapshot_projection(new, ['id'])
    assert old_meta['keys'] == new_meta['keys'] == []
    result = shared.compare_source_snapshot_evidence(current, previous, keyed=False)
    assert (result['added_count'], result['removed_count'], result['modified_count']) == (2, 1, None)
    assert result['ambiguous_count'] == 1 and result['ambiguous_count_overlaps_removed']


@pytest.mark.parametrize('keys,rows', [(['absent'], [(1, 'a')]), (['id', 'id'], [(1, 'a')]),
    (['id'], [(None, 'a')]), (['id'], [(1, 'a'), (1, 'b')])])
def test_missing_null_or_ambiguous_authored_keys_fall_back_to_content(spark_session, keys, rows):
    frame = spark_session.createDataFrame(rows, 'id int, value string')
    evidence, metadata = shared.source_snapshot_projection(frame, keys)
    assert metadata['keys'] == []
    assert shared._source_evidence_totals(evidence)['rows'] == len(rows)


def test_typed_content_hash_includes_business_ingestion_fields(spark_session):
    original = spark_session.createDataFrame([(1, 'run-a', 'value')], 'id int, JobId string, payload string')
    changed = spark_session.createDataFrame([(1, 'run-b', 'value')], original.schema)
    previous, _ = shared.source_snapshot_projection(original, ['id'])
    current, _ = shared.source_snapshot_projection(changed, ['id'])
    assert shared.compare_source_snapshot_evidence(current, previous, keyed=True)['modified_count'] == 1


def test_hash_diagnostics_are_bounded_while_aggregate_counts_cover_all_rows(spark_session):
    old = spark_session.createDataFrame([(n, 'before') for n in range(25)], 'id int, value string')
    new = spark_session.createDataFrame([(n, 'after') for n in range(25)], old.schema)
    previous, _ = shared.source_snapshot_projection(old, ['id'])
    current, _ = shared.source_snapshot_projection(new, ['id'])
    result = shared.compare_source_snapshot_evidence(current, previous, keyed=True)
    assert result['modified_count'] == 25 and len(result['samples']['modified']) == 10
    assert 'before' not in str(result['samples']) and 'after' not in str(result['samples'])


@pytest.mark.parametrize('authored,expected', [(False, []), (True, ['id'])])
def test_sampled_discovery_never_supplies_source_drift_identity(authored, expected):
    import json
    from types import SimpleNamespace
    payload = {'table': {'columns': [{'column_id': 'id-column', 'column_name': 'id'}]},
        'guardrails': [{'guardrail_type': 'grain', 'is_active': True, 'rule_parameters': {'columns': ['id-column']}}] if authored else []}
    plan = SimpleNamespace(contracts_json=json.dumps({'source': {'contract_payload': payload}}))
    identity = {'table_id': 'source', 'load_strategy_parameters_json': {},
        'grain_candidates_json': {'profile_scope': 'bounded_sample', 'candidates': [{'columns': ['id']}]}}
    assert shared._source_snapshot_keys(identity, {'execution_plan': plan}) == expected


def test_snapshot_filter_keeps_invalid_legacy_rows_for_fail_closed_validation(spark_session):
    from pyspark.sql.types import StructField, StructType
    schema = StructType([StructField(field.name, field.dataType, True)
        for field in shared.metadata_table_schema_registry()[shared._PROCESSING_STATE_TABLE]])
    legacy = {'workspace_id': 'dev', 'record_id': 'checkpoint', 'record_type': 'incremental_checkpoint', 'status': 'committed'}
    snapshot = {'workspace_id': 'dev', 'record_id': 'hash', 'record_type': 'source_row_evidence', 'status': 'observed'}
    corrupt = {'workspace_id': 'dev', 'record_id': 'invalid', 'record_type': None, 'status': 'committed'}
    valid = spark_session.createDataFrame([legacy, snapshot], schema)
    assert [row['record_id'] for row in shared._processing_state_rows(valid)] == ['checkpoint']
    with pytest.raises(RuntimeError, match='invalid METADATA_PROCESSING_STATE'):
        shared._processing_state_rows(spark_session.createDataFrame([legacy, snapshot, corrupt], schema))
