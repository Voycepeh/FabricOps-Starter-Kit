"""Lossless physical JSON metadata and stable logical approval evidence."""

from datetime import UTC, datetime, timedelta, timezone
import json

import pytest

from fabricops_kit.activated_pipeline.shared import manifest_digest
from fabricops_kit.config.metadata_schemas import (
    decode_metadata_row, encode_metadata_row, metadata_json_schema,
    metadata_schema_type_name, metadata_table_schema_registry,
)
from fabricops_kit.pipeline.shared import pipeline_record_content, validate_pipeline_run

RUN = 'METADATA_PIPELINE_RUN'
CATALOGUE = 'METADATA_DATA_CATALOGUE'


def logical_run():
    """Return representative retained Run facts, including nested nulls/timestamps."""
    return decode_metadata_row(RUN, {
        'run_id': 'retained-run', 'status': 'incomplete',
        'operations': [{'operation_key': 'source:orders', 'table_id': 'orders', 'pipeline_role': 'source',
            'contract_id': 'contract', 'contract_version': 7, 'payload_sha256': 'unchanged',
            'destination': {'workspace_id': 'environment', 'item_id': 'lakehouse', 'kind': 'lakehouse',
                'schema': None, 'table_name': '订单'}, 'read_mode': 'full', 'source_table_ids': [],
            'status': 'succeeded', 'started_at': datetime(2020, 1, 2, 3, 4, 5, 123456),
            'completed_at': datetime(2020, 1, 2, 3, 5, 5, 123456),
            'stages': [{'stage': 'Read', 'status': 'passed'}]}],
        'profiling': [{'context_key': 'physical', 'activity': 'frequency', 'status': 'passed',
            'results_persisted': True, 'empty_result': True, 'row_count': 2**60,
            'completed_at': '2020-01-02T03:05:05+00:00'}],
        'failures': [{'code': 'safe_failure', 'exception_type': None}, {'code': 'safe_failure'}],
    })


def test_six_columns_are_physically_strings_and_registry_is_scalar():
    """Physical JSON does not create a reporting table or introduce nested Registry authority."""
    physical = metadata_table_schema_registry()
    assert len(physical) == 14
    for table in (RUN, CATALOGUE):
        assert all(metadata_schema_type_name(field.dataType) == 'string'
                   for field in physical[table].fields if field.name in metadata_json_schema(table))
    assert all(not hasattr(field.dataType, 'elementType') for field in physical['METADATA_PIPELINE_REGISTRY'])


def test_retained_run_hash_and_python_interfaces_survive_json_roundtrip():
    """Hash-bearing logical evidence is identical after physical persistence."""
    before = logical_run()
    physical = encode_metadata_row(RUN, before)
    assert all(isinstance(physical[name], str) for name in metadata_json_schema(RUN))
    after = validate_pipeline_run(physical)
    assert pipeline_record_content(after) == pipeline_record_content(before)
    assert manifest_digest({'run': after, 'guardrail_results': []}) == manifest_digest({'run': before, 'guardrail_results': []})
    assert len(after['failures']) == 2
    assert after['operations'][0]['destination']['table_name'] == '订单'
    assert after['profiling'][0]['row_count'] == 2**60


def test_json_bytes_are_retained_for_compare_and_swap():
    """Valid historical whitespace/key order must not invalidate expected Run bytes."""
    physical = encode_metadata_row(RUN, logical_run())
    physical['operations'] = json.dumps(json.loads(physical['operations']), indent=2, sort_keys=False)
    assert encode_metadata_row(RUN, physical) == physical
    assert decode_metadata_row(RUN, physical) == logical_run()


def test_timestamps_preserve_microseconds_and_utc_instants():
    """Offset instants normalize exactly like existing approval content hashing."""
    row = logical_run()
    instant = datetime(2020, 1, 2, 3, 4, 5, 999999, tzinfo=timezone(timedelta(hours=8)))
    row['operations'][0]['started_at'] = instant
    after = decode_metadata_row(RUN, encode_metadata_row(RUN, row))
    assert after['operations'][0]['started_at'] == instant.astimezone(UTC).replace(tzinfo=None)
    assert pipeline_record_content(row) == pipeline_record_content(after)


@pytest.mark.parametrize('value', [None, [], {}, {'key_columns': []}, {'key_columns': ['tenant', 'id']}])
def test_catalogue_null_empty_and_order(value):
    """SQL null and explicit empty values retain the typed Catalogue meaning."""
    field = 'load_strategy_parameters_json'
    if isinstance(value, list):
        with pytest.raises(ValueError, match='object'):
            encode_metadata_row(CATALOGUE, {field: value})
        return
    row = {field: value, 'untouched': 'retain'}
    result = decode_metadata_row(CATALOGUE, encode_metadata_row(CATALOGUE, row))
    assert result == decode_metadata_row(CATALOGUE, row)
    assert (result[field] is None) == (value is None)


@pytest.mark.parametrize('payload', ['null', '"[]"', '{}', '[null]', '[{"code":"x","code":"y"}]',
                                       '[{"code":"x","unknown":true}]', '[{"code":3}]', 'NaN', ''])
def test_run_invalid_json_fails_closed(payload):
    """No permissive JSON parser can fabricate valid run failure facts."""
    with pytest.raises(ValueError):
        decode_metadata_row(RUN, {'failures': payload})


@pytest.mark.parametrize('value', [2**63, 1.5, True, float('inf')])
def test_discovery_counts_never_undergo_lossy_numeric_coercion(value):
    """Bigint bounds and integer semantics survive migration and writes."""
    with pytest.raises(ValueError):
        encode_metadata_row(CATALOGUE, {'profile_key_candidates_json': {'candidates': [{'row_count': value}]}})


@pytest.mark.spark
def test_spark_history_decode_rejects_corrupt_nonnull_json(spark_session):
    """Malformed profiling cannot disappear as an empty scheduling history."""
    from fabricops_kit.config.metadata_schemas import decode_metadata_dataframe
    frame = spark_session.createDataFrame([('{"unexpected":"object"}',)], 'profiling string')
    with pytest.raises(Exception, match='profiling must be an array'):
        decode_metadata_dataframe(RUN, frame).select('profiling').collect()


def test_historical_append_run_facts_keep_their_exact_hash():
    """Retained operation facts remain readable without accepting append for new processing."""
    from fabricops_kit.pipeline.shared import validated_processing
    before = logical_run()
    before['operations'][0].update(operation_key='target:orders', pipeline_role='target', read_mode=None, write_mode='append')
    digest = manifest_digest(before)
    after = validate_pipeline_run(encode_metadata_row(RUN, before))
    assert manifest_digest(after) == digest
    assert after['operations'][0]['write_mode'] == 'append'
    with pytest.raises(ValueError, match='invalid load_strategy'):
        validated_processing({'load_strategy': 'append'})


def test_retained_profile_events_do_not_acquire_scope_fields_or_change_hashes():
    """Additive profiling scope must preserve exact historical logical Run content."""
    retained = logical_run()
    for event in retained['profiling']:
        event.pop('profile_scope', None)
        event.pop('profiling_max_rows', None)
    expected_digest = manifest_digest(retained)
    encoded = encode_metadata_row(RUN, retained)
    decoded = validate_pipeline_run(encoded)
    assert decoded == retained
    assert manifest_digest(decoded) == expected_digest
    scoped = {**retained, 'profiling': [{**retained['profiling'][0],
        'profile_scope': 'bounded_selection', 'profiling_max_rows': 100}]}
    assert decode_metadata_row(RUN, encode_metadata_row(RUN, scoped)) == scoped


def test_pre_file_write_run_retains_released_content_hash():
    """Decode a fixture exported on main before the file-write schema additions."""
    from pathlib import Path
    fixture = json.loads((Path(__file__).parents[1] / 'fixtures' / 'retained_run_before_file_writes.json').read_text())
    physical = fixture['physical_run']
    decoded = decode_metadata_row(RUN, physical)
    assert manifest_digest(decoded) == fixture['logical_sha256']
    operation = decoded['operations'][0]
    assert all(key not in operation for key in ('file_write_parameters_json', 'output_path', 'publication_status'))
    assert all(key not in operation['metrics'] for key in ('file_count', 'output_bytes'))
    assert encode_metadata_row(RUN, decoded) == physical
    assert encode_metadata_row(RUN, physical) == physical


def test_explicit_file_write_fields_survive_run_roundtrip():
    """Preserve both absent historical fields and explicitly present file facts."""
    row = logical_run()
    operation = row['operations'][0]
    operation.update(file_write_parameters_json='{"single_file":true}', output_path='configured/Files/orders.csv',
                     publication_status='published', metrics={'file_count': 1, 'output_bytes': 12})
    decoded = decode_metadata_row(RUN, encode_metadata_row(RUN, row))
    actual = decoded['operations'][0]
    for field in ('file_write_parameters_json', 'output_path', 'publication_status'):
        assert actual[field] == operation[field]
    assert actual['metrics']['file_count'] == 1 and actual['metrics']['output_bytes'] == 12
