"""Strict Catalogue values and identical schema references with optional Spark."""
import importlib
import json
import os
import subprocess
import sys

import pytest

from fabricops_kit.config.metadata_schemas import (
    CATALOGUE_NESTED_FIELDS, coerce_metadata_row_types, metadata_table_schema_registry,
    metadata_table_schema_rows,
)

migration = importlib.import_module('fabricops_kit.config.setup_metadata_tables')


def test_schema_and_type_documentation_are_identical_without_pyspark():
    """Fallback schemas describe every nested field with the same stable labels."""
    expected = metadata_table_schema_rows(metadata_table_schema_registry()['METADATA_DATA_CATALOGUE'])
    code = '''
import sys, json
class NoSpark:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'pyspark' or fullname.startswith('pyspark.'):
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, NoSpark())
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry, metadata_table_schema_rows
print(json.dumps(metadata_table_schema_rows(metadata_table_schema_registry()['METADATA_DATA_CATALOGUE'])))
'''
    actual = subprocess.check_output([sys.executable, '-c', code], env={**os.environ, 'PYTHONPATH': 'src'}, text=True)
    assert json.loads(actual) == expected
    types = {item['name']: item['type'] for item in expected}
    assert types['load_strategy_parameters_json'] == (
        'struct<watermark_column:string,key_columns:array<string>,effective_column:string,tracked_columns:array<string>>')
    assert types['scheduled_refresh_json'] == (
        'struct<status:string,schedules:array<struct<enabled:boolean,frequency:string,times:array<string>,timezone:string>>>')
    assert types['profile_key_candidates_json'] == (
        'struct<status:string,max_combination_width:int,candidates:array<struct<columns:array<string>,'
        'column_count:int,row_count:bigint,distinct_count:bigint,uniqueness_percent:double,null_count:bigint>>>')


@pytest.mark.parametrize(('field', 'value'), [
    ('load_strategy_parameters_json', '{"watermark_column":false}'),
    ('load_strategy_parameters_json', '[]'),
    ('load_strategy_parameters_json', '{"key_columns":"id"}'),
    ('scheduled_refresh_json', '{"schedules":[false]}'),
    ('scheduled_refresh_json', '{"schedules":{}}'),
    ('profile_key_candidates_json', '{"status":3}'),
    ('profile_key_candidates_json', '{"candidates":[{"row_count":9223372036854775808}]}'),
    ('profile_key_candidates_json', '{"candidates":[{"uniqueness_percent":NaN}]}'),
    ('profile_key_candidates_json', '{"candidates":[{"uniqueness_percent":1e999}]}'),
    ('profile_key_candidates_json', '{"candidates":[{"unknown":1}]}'),
])
def test_strict_historical_parser_rejects_lossy_values(field, value):
    """Spark's permissive string/numeric/null coercions are never migration rules."""
    schema = metadata_table_schema_registry()['METADATA_DATA_CATALOGUE']
    kind = next(item.dataType for item in schema.fields if item.name == field)
    with pytest.raises(ValueError):
        migration._parse_catalogue_value(value, kind, field=field, historical=True)


@pytest.mark.parametrize('field', CATALOGUE_NESTED_FIELDS)
def test_runtime_coercion_requires_native_structs_and_rejects_unknown_fields(field):
    """Historical JSON compatibility is confined to setup migration."""
    for value in ('{}', {'unknown': 1}, []):
        with pytest.raises(ValueError):
            coerce_metadata_row_types('METADATA_DATA_CATALOGUE', {field: value})
    assert coerce_metadata_row_types('METADATA_DATA_CATALOGUE', {field: None})[field] is None
    assert all(value is None for value in coerce_metadata_row_types('METADATA_DATA_CATALOGUE', {field: {}})[field].values())


def test_unrelated_custom_json_fields_remain_strings():
    """Steward and Agreement JSON are outside this conversion."""
    for table in ('METADATA_DATA_STEWARD', 'METADATA_DATA_AGREEMENT'):
        result = coerce_metadata_row_types(table, {'custom_fields_json': '{"retain":[1,2]}'})
        assert result['custom_fields_json'] == '{"retain":[1,2]}'
