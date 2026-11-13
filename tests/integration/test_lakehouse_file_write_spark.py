"""Exercise real Spark output and Hadoop publication with local storage."""
# ruff: noqa: D103
import importlib
from pathlib import Path

import pytest

from fabricops_kit import write_lakehouse_file

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
