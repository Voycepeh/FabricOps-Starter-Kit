"""Exercise real Spark output and Hadoop publication with local storage."""
# ruff: noqa: D103
import importlib
from pathlib import Path

import pytest

from fabricops_kit import write_lakehouse_file, orchestrate_write, setup_pipeline, finalize_pipeline
from tests.unit.test_pipeline_session import runtime  # noqa: F401
from tests.unit.test_unified_file_read import files  # noqa: F401

pytestmark = pytest.mark.spark


@pytest.mark.parametrize('fmt', ['csv', 'parquet', 'json'])
@pytest.mark.parametrize('single', [False, True])
@pytest.mark.parametrize('empty', [False, True])
def test_real_spark_file_output(spark_session, monkeypatch, tmp_path, fmt, single, empty):
    owner = importlib.import_module('fabricops_kit.io.write_lakehouse_file')
    monkeypatch.setattr(owner, 'resolve_configured_file_path', lambda store, path, **kw: (None, path, str(tmp_path / path)))
    frame = spark_session.createDataFrame([(1, 'first'), (2, 'second')], 'id long, value string').repartition(2)
    if empty:
        frame = frame.limit(0)
    if not single and not empty:
        monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_ROWS', 1)
    result = write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt,
        write_options={'header': True} if fmt == 'csv' else {}, verbose=False)
    destination = Path(result['resolved_path'])
    expected_single = single or empty
    assert destination.is_file() if expected_single else destination.is_dir()
    assert result['write_metrics']['file_count'] >= 1
    assert result['write_metrics']['output_bytes'] >= 0
    assert not list(destination.parent.glob('*.fabricops-*'))
    reader = spark_session.read.format(fmt)
    if fmt == 'csv':
        reader = reader.option('header', True).schema(frame.schema)
    elif fmt == 'json':
        reader = reader.schema(frame.schema)
    assert reader.load(str(destination)).count() == (0 if empty else 2)
    if expected_single:
        with pytest.raises(ValueError, match='dataset folder'):
            write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt,
                                 mode='append_all', verbose=False)
    else:
        appended = write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt,
                                        mode='append_all', verbose=False,
                                        write_options={'header': True} if fmt == 'csv' else {})
        assert appended['output_layout'] == 'dataset_folder' and appended['overflow_reason'] is None
        assert reader.load(str(destination)).count() == 4
    replaced = write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt,
                                    mode='overwrite', verbose=False,
                                    write_options={'header': True} if fmt == 'csv' else {})
    assert replaced['published'] is True
    assert reader.load(str(destination)).count() == (0 if empty else 2)


@pytest.mark.parametrize('fmt', ['csv', 'parquet', 'json'])
@pytest.mark.parametrize('single', [False, True])
def test_overwrite_finishes_lazy_input_before_replacing_destination(spark_session, monkeypatch, tmp_path, fmt, single):
    owner = importlib.import_module('fabricops_kit.io.write_lakehouse_file')
    monkeypatch.setattr(owner, 'resolve_configured_file_path', lambda store, path, **kw: (None, path, str(tmp_path / path)))
    relative = 'nested/orders.' + fmt
    if not single:
        monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_ROWS', 1)
    original = spark_session.createDataFrame([(1,), (2,)], 'id long')
    options = {'header': True} if fmt == 'csv' else {}
    write_lakehouse_file(original, relative, file_format=fmt, write_options=options, verbose=False)
    reader = spark_session.read.format(fmt).schema(original.schema)
    if fmt == 'csv':
        reader = reader.option('header', True)
    # This DataFrame must remain lazy until the overwrite function evaluates it.
    source = reader.load(str(tmp_path / relative)).selectExpr('id + 10 as id')
    result = write_lakehouse_file(source, relative, file_format=fmt,
        write_options=options, mode='overwrite', verbose=False)
    assert result['published'] is True
    assert sorted(row.id for row in reader.load(result['resolved_path']).collect()) == [11, 12]
    assert not list((tmp_path / 'nested').glob('*.fabricops-*'))



@pytest.mark.parametrize('single', [False, True])
def test_orchestrated_overwrite_profiles_lazy_source_before_publication(files, spark_session, monkeypatch, tmp_path, single):  # noqa: F811
    from datetime import datetime
    from fabricops_kit.pipeline import shared
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    audit = {field.name: datetime(2026, 1, 1) if field.name == '_committed_at' else 'audit-' + field.name
             for field in metadata_table_schema_registry()['METADATA_DATA_PROFILED'] if field.name.startswith('_')}
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kw: dict(audit))
    snapshots = []
    monkeypatch.setattr(shared, '_replace_snapshot_rows', lambda **kw: snapshots.extend(kw['dataframe'].collect()))

    def read_catalogue(table, **_kwargs):
        assert table == "METADATA_DATA_CATALOGUE"
        identity = files.catalogue.call_args.args[0]
        return spark_session.createDataFrame(
            [(identity["workspace_id"], identity["table_id"], "FILE", True)],
            "asset_workspace_id string, table_id string, asset_type string, is_active boolean",
        )

    reader = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    monkeypatch.setattr(reader, "read_lakehouse_table", read_catalogue)
    routing = importlib.import_module('fabricops_kit.io.shared')
    owner = importlib.import_module('fabricops_kit.io.write_lakehouse_file')
    def resolve(store, path, **kwargs):
        return files.configured, path, str(tmp_path / path)
    monkeypatch.setattr(routing, 'resolve_configured_file_path', resolve)
    monkeypatch.setattr(owner, 'resolve_configured_file_path', resolve)
    if not single:
        monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_ROWS', 1)
    original = spark_session.createDataFrame([(1,), (2,)], 'id long')
    write_lakehouse_file(original, 'orders.parquet', verbose=False)
    source = spark_session.read.parquet(str(tmp_path / 'orders.parquet')).selectExpr('id + 10 as id')
    session = setup_pipeline(pipeline_mode='Ungoverned')
    result = orchestrate_write(source, store='Silver', relative_path='orders.parquet', file_format='parquet',
        write_mode='overwrite')
    assert result['published'] is True and result['profile_result']['row_count'] == 2
    assert result['profile_result']['results_persisted'] is True
    assert snapshots and all(row.asset_type == 'FILE' and row.table_id.startswith('file:') and row.column_id is not None for row in snapshots)
    assert result['profile_result']['profile'].select('ROW_COUNT').first()[0] == 2
    assert result['profile_result']['profile'].select('MIN_VALUE').first()[0] == '11'
    assert [stage['stage'] for stage in result['orchestration_stages']] == ['Profile', 'Write']
    assert sorted(row.id for row in spark_session.read.parquet(result['resolved_path']).collect()) == [11, 12]
    assert finalize_pipeline(session)['status'] == 'ungoverned_completed'


@pytest.mark.parametrize('fmt', ['csv', 'json', 'parquet'])
@pytest.mark.parametrize('limit', ['rows', 'bytes'])
@pytest.mark.parametrize('old_single', [False, True])
def test_overflow_preserves_all_lazy_input_rows_at_exact_path(spark_session, monkeypatch, tmp_path, fmt, limit, old_single):
    owner = importlib.import_module('fabricops_kit.io.write_lakehouse_file')
    monkeypatch.setattr(owner, 'resolve_configured_file_path', lambda store, path, **kw: (None, path, str(tmp_path / path)))
    relative = 'nested/orders.' + fmt
    original = spark_session.createDataFrame([(index, 'value-' + str(index)) for index in range(9)], 'id long, value string').repartition(2)
    options = {'header': True} if fmt == 'csv' else {}
    monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_ROWS', 1_000_000 if old_single else 2)
    write_lakehouse_file(original, relative, file_format=fmt, write_options=options, verbose=False)
    reader = spark_session.read.format(fmt).schema(original.schema)
    if fmt == 'csv':
        reader = reader.option('header', True)
    source = reader.load(str(tmp_path / relative)).selectExpr('id + 10 as id', 'value').repartition(2)
    monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_ROWS', 2 if limit == 'rows' else 1_000_000)
    monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_BYTES', 1 if limit == 'bytes' else 100_000_000)
    result = write_lakehouse_file(source, relative, file_format=fmt, write_options=options, repartition_by=3, verbose=False)
    destination = tmp_path / relative
    assert destination.is_dir() and result['resolved_path'] == str(destination)
    assert result['output_layout'] == 'dataset_folder' and result['overflow_occurred'] is True
    assert result['overflow_reason'] == ('row_limit' if limit == 'rows' else 'byte_limit')
    expected = [(index + 10, 'value-' + str(index)) for index in range(9)]
    assert sorted(tuple(row) for row in reader.load(str(destination)).collect()) == expected
    parts = list(destination.glob('part-*'))
    assert result['write_metrics']['file_count'] == len(parts) == 3
    assert result['write_metrics']['output_bytes'] == sum(part.stat().st_size for part in parts)
    assert not list(destination.parent.glob('*.fabricops-*'))
    assert not list(destination.parent.glob('*_parts*'))
    # A small default write safely converts the dataset folder back to a file,
    # including a lazy read of that folder as its input.
    small = reader.load(str(destination)).where('id = 10')
    monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_BYTES', 100_000_000)
    replacement = write_lakehouse_file(small, relative, file_format=fmt, write_options=options, verbose=False)
    assert destination.is_file() and replacement['output_layout'] == 'single_file'
    assert replacement['overflow_occurred'] is False
    assert [tuple(row) for row in reader.load(str(destination)).collect()] == [expected[0]]
    assert not list(destination.parent.glob('*.fabricops-*'))
