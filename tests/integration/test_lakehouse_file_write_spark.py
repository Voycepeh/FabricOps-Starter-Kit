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
    result = write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt, single_file=single,
        write_options={'header': True} if fmt == 'csv' else {}, verbose=False)
    destination = Path(result['resolved_path'])
    assert destination.is_file() if single else destination.is_dir()
    assert result['write_metrics']['file_count'] >= 1
    assert result['write_metrics']['output_bytes'] >= 0
    assert not list(destination.parent.glob('*.fabricops-*'))
    reader = spark_session.read.format(fmt)
    if fmt == 'csv':
        reader = reader.option('header', True).schema(frame.schema)
    elif fmt == 'json':
        reader = reader.schema(frame.schema)
    assert reader.load(str(destination)).count() == (0 if empty else 2)
    ignored = write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt, single_file=single, mode='ignore', verbose=False)
    assert ignored['published'] is False
    with pytest.raises(FileExistsError):
        write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt, single_file=single, verbose=False)
    if not single:
        write_lakehouse_file(frame, 'nested/orders.' + fmt, file_format=fmt, mode='append', verbose=False,
            write_options={'header': True} if fmt == 'csv' else {})
        assert reader.load(str(destination)).count() == (0 if empty else 4)


@pytest.mark.parametrize('fmt', ['csv', 'parquet', 'json'])
@pytest.mark.parametrize('single', [False, True])
def test_overwrite_finishes_lazy_input_before_replacing_destination(spark_session, monkeypatch, tmp_path, fmt, single):
    owner = importlib.import_module('fabricops_kit.io.write_lakehouse_file')
    monkeypatch.setattr(owner, 'resolve_configured_file_path', lambda store, path, **kw: (None, path, str(tmp_path / path)))
    relative = 'nested/orders.' + fmt
    original = spark_session.createDataFrame([(1,), (2,)], 'id long')
    options = {'header': True} if fmt == 'csv' else {}
    write_lakehouse_file(original, relative, file_format=fmt, single_file=single, write_options=options, verbose=False)
    reader = spark_session.read.format(fmt).schema(original.schema)
    if fmt == 'csv':
        reader = reader.option('header', True)
    # This DataFrame must remain lazy until the overwrite function evaluates it.
    source = reader.load(str(tmp_path / relative)).selectExpr('id + 10 as id')
    result = write_lakehouse_file(source, relative, file_format=fmt, single_file=single,
        write_options=options, mode='overwrite', verbose=False)
    assert result['published'] is True
    assert sorted(row.id for row in reader.load(result['resolved_path']).collect()) == [11, 12]
    assert not list((tmp_path / 'nested').glob('*.fabricops-*'))



@pytest.mark.parametrize('single', [False, True])
def test_orchestrated_overwrite_profiles_lazy_source_before_publication(files, spark_session, monkeypatch, tmp_path, single):  # noqa: F811
    routing = importlib.import_module('fabricops_kit.io.shared')
    owner = importlib.import_module('fabricops_kit.io.write_lakehouse_file')
    def resolve(store, path, **kwargs):
        return files.configured, path, str(tmp_path / path)
    monkeypatch.setattr(routing, 'resolve_configured_file_path', resolve)
    monkeypatch.setattr(owner, 'resolve_configured_file_path', resolve)
    original = spark_session.createDataFrame([(1,), (2,)], 'id long')
    write_lakehouse_file(original, 'orders.parquet', single_file=single, verbose=False)
    source = spark_session.read.parquet(str(tmp_path / 'orders.parquet')).selectExpr('id + 10 as id')
    session = setup_pipeline(pipeline_mode='Ungoverned')
    result = orchestrate_write(source, store='Silver', relative_path='orders.parquet', file_format='parquet',
        single_file=single, write_mode='overwrite')
    assert result['published'] is True and result['profile_result']['row_count'] == 2
    assert [stage['stage'] for stage in result['orchestration_stages']] == ['Profile', 'Write']
    assert sorted(row.id for row in spark_session.read.parquet(result['resolved_path']).collect()) == [11, 12]
    assert finalize_pipeline(session)['status'] == 'ungoverned_completed'
