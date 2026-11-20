"""One asset identity across current metadata, with verifiable retained history."""
from copy import deepcopy
import hashlib
import json

import pytest

from fabricops_kit.config.metadata_schemas import (
    decode_metadata_row, encode_metadata_row, metadata_table_schema_registry, migrate_asset_references,
)
from fabricops_kit.data_contract.shared import file_source_identity
from fabricops_kit.pipeline.shared import validate_pipeline_run
from fabricops_kit.activated_pipeline.shared import manifest_digest, validate_submission
from tests.unit.test_pipeline_handoff import package_candidate, resign


def test_every_current_asset_owner_uses_the_same_identity_fields():
    """Asset owners share the common key without duplicating record primary keys."""
    registry = metadata_table_schema_registry(logical=True)
    for name in ('DATA_CATALOGUE', 'DATA_CONTRACT', 'DATA_CONTRACT_ACTIVATION', 'DATA_PROFILED',
                 'DATA_PROFILED_FREQUENCY', 'DATA_ACCESS', 'GUARDRAIL_RESULTS'):
        fields = registry['METADATA_' + name].fieldNames()
        assert {'table_id', 'asset_type'} <= set(fields)
        assert 'source_id' not in fields
    operation = registry['METADATA_PIPELINE_RUN']['operations'].dataType.elementType
    assert {'table_id', 'asset_type', 'source_assets'} <= set(operation.fieldNames())
    assert not {'source_id', 'source_type', 'source_ids', 'source_table_ids'} & set(operation.fieldNames())
    assert set(operation['source_assets'].dataType.elementType.fieldNames()) == {'table_id', 'asset_type'}


def test_file_identity_and_frozen_payload_bytes_survive_interpretation():
    """The field migration retains the selector hash and does not touch frozen text."""
    physical = {'workspace_id': 'w', 'item_id': 'i', 'relative_path': 'incoming/orders.csv'}
    original_id = 'file:' + hashlib.sha256(json.dumps(physical, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    source = file_source_identity(**physical, file_format='csv')
    assert source['table_id'] == original_id and source['asset_type'] == 'FILE'
    frozen = '{ "source" : {"source_id":"' + original_id + '", "source_type":"file"} }'
    original = {'table_id': None, 'source_id': original_id, 'contract_payload_json': frozen}
    migrated = migrate_asset_references(original)
    assert migrated == {'table_id': original_id, 'asset_type': 'FILE', 'contract_payload_json': frozen}
    assert original['table_id'] is None and original['source_id'] == original_id
    with pytest.raises(ValueError, match='Conflicting'):
        migrate_asset_references({**original, 'table_id': 'other'})


def test_retained_run_operations_and_hash_do_not_change():
    """Version 3 remains queryable without rewriting its released identity fields."""
    run = package_candidate()['dry_run']
    run['run_schema_version'] = 3
    for operation in run['operations']:
        operation['source_table_ids'] = [ref['table_id'] for ref in operation.pop('source_assets')]
        operation.pop('asset_type')
    physical = {**run, 'operations': json.dumps(run['operations'], indent=3),
                'profiling': json.dumps(run['profiling'], indent=2), 'failures': json.dumps(run['failures'])}
    before = deepcopy(physical)
    decoded = validate_pipeline_run(physical)
    assert 'asset_type' not in decoded['operations'][0]
    assert encode_metadata_row('METADATA_PIPELINE_RUN', physical) == before
    assert manifest_digest(decoded) == manifest_digest(run)
    modern = {**physical, 'run_schema_version': 4}
    with pytest.raises(ValueError, match='version 4'):
        decode_metadata_row('METADATA_PIPELINE_RUN', modern)


def test_legacy_submission_is_verified_without_changing_its_approved_digest():
    """Old packages retain their format and digest while new packages use format 2."""
    package = package_candidate()
    assert package['manifest']['format_version'] == 2
    package['manifest']['format_version'] = 1
    for operations in (package['manifest']['operations'], package['manifest']['tested_operations'], package['dry_run']['operations']):
        for operation in operations:
            if 'source_assets' not in operation:
                continue
            operation['source_table_ids'] = [ref['table_id'] for ref in operation.pop('source_assets')]
            operation.pop('asset_type')
    resign(package)
    original = deepcopy(package)
    assert validate_submission(json.dumps(package)) == original
    changed = deepcopy(original)
    changed['manifest']['parameters']['manual'] = True
    with pytest.raises(ValueError, match='digest'):
        validate_submission(changed)


def test_authored_fields_are_opaque_during_historical_interpretation():
    """Business parameters named like metadata identity fields remain untouched."""
    options = {"source_id": "business-column", "source_type": "table", "table_id": "label"}
    payload = {"reader_options": options, "parameters": options,
               "guardrails": [{"parameters": options}], "enrichment": {"table": [options]},
               "source": {"source_id": "file:retained", "source_type": "file", "reader_options": options}}
    interpreted = migrate_asset_references(payload)
    assert interpreted["source"]["table_id"] == "file:retained"
    assert interpreted["source"]["reader_options"] == options
    for key in ("reader_options", "parameters", "guardrails", "enrichment"):
        assert interpreted[key] == payload[key]


def test_retained_file_run_preserves_json_and_projects_common_identity():
    """File operations and split input lists remain immutable in version 3."""
    source = file_source_identity(workspace_id='physical', item_id='lakehouse',
                                  relative_path='incoming/orders.csv', file_format='csv')
    run = package_candidate()['dry_run']
    run['run_schema_version'] = 3
    target = run['operations'][0]
    target.pop('asset_type')
    target.pop('source_assets')
    target.update(source_table_ids=[], source_ids=[source['table_id']])
    file_operation = deepcopy(target)
    file_operation.update(operation_key='source:Bronze/Files/incoming/orders.csv', table_id=None,
                          source_id=source['table_id'], source_type='file', pipeline_role='source',
                          read_mode='full', write_mode=None, source_ids=[],
                          destination={**{key: value for key, value in source.items() if key not in {'reader_options', 'asset_type', 'table_id'}},
                                       'source_type': 'file', 'source_id': source['table_id'], 'reader_options_json': '{}'})
    run['operations'].insert(0, file_operation)
    physical = {**run, 'operations': json.dumps(run['operations'], indent=2), 'profiling': '[]', 'failures': '[]'}
    before = deepcopy(physical)
    retained = validate_pipeline_run(physical)
    assert encode_metadata_row('METADATA_PIPELINE_RUN', physical) == before
    assert manifest_digest(retained) == manifest_digest(run)
    interpreted = migrate_asset_references(retained)
    assert interpreted['operations'][0]['table_id'] == source['table_id']
    assert interpreted['operations'][0]['asset_type'] == 'FILE'
    assert interpreted['operations'][1]['source_assets'] == [{'table_id': source['table_id'], 'asset_type': 'FILE'}]
