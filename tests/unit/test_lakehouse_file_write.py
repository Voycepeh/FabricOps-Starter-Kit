"""Exact file publication and pipeline lifecycle coverage without Fabric services."""
# ruff: noqa: D102, D103, D105, D107, F811
import importlib
from pathlib import PurePosixPath
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit import write_lakehouse_file, orchestrate_write, orchestrate_read, setup_pipeline, finalize_pipeline
from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_session import runtime  # noqa: F401
from tests.unit.test_unified_file_read import files  # noqa: F401


class Path:
    """Small Hadoop Path test double."""

    def __init__(self, value):
        self.value = str(value)

    def __str__(self):
        return self.value

    def getName(self):  # noqa: N802
        return PurePosixPath(self.value).name

    def getParent(self):  # noqa: N802
        return Path(str(PurePosixPath(self.value).parent))


class Filesystem:
    """Track collision and publication calls using physical file entries."""

    def __init__(self):
        self.entries = {}
        self.deleted = []
        self.renames = []

    def exists(self, path):
        return str(path) in self.entries

    def isFile(self, path):  # noqa: N802
        return self.entries[str(path)] is not None

    def delete(self, path, recursive):
        self.deleted.append(str(path))
        for key in list(self.entries):
            if key == str(path) or recursive and key.startswith(str(path) + '/'):
                del self.entries[key]
        return True

    def mkdirs(self, path):
        self.entries[str(path)] = None
        return True

    def rename(self, source, target):
        self.renames.append((str(source), str(target)))
        source, target = str(source), str(target)
        for key in list(self.entries):
            if key == source or key.startswith(source + '/'):
                self.entries[target + key[len(source):]] = self.entries.pop(key)
        return True

    def listStatus(self, path):  # noqa: N802
        return [SimpleNamespace(isFile=lambda: True, getPath=lambda key=key: Path(key), getLen=lambda size=size: size)
                for key, size in self.entries.items() if key.startswith(str(path) + '/') and size is not None]

    def listFiles(self, path, recursive):  # noqa: N802
        entries = self.listStatus(path) if not self.isFile(path) else [SimpleNamespace(getPath=lambda: path, getLen=lambda: self.entries[str(path)])]
        iterator = iter(entries)
        remaining = list(iterator)
        return SimpleNamespace(hasNext=lambda: bool(remaining), next=lambda: remaining.pop(0))


@pytest.fixture
def output(monkeypatch):
    owner = importlib.import_module('fabricops_kit.io.write_lakehouse_file')
    fs = Filesystem()
    frame = Mock(columns=['id'])
    frame.repartition.return_value = frame
    frame.coalesce.return_value = frame
    frame.limit.return_value.count.return_value = 2
    writer = frame.write
    writer.format.return_value = writer
    writer.mode.return_value = writer
    writer.options.return_value = writer
    def save(path):
        fs.entries[str(path)] = None
        fs.entries[str(path) + '/part-00000.csv'] = 12
    writer.save.side_effect = save
    monkeypatch.setattr(owner, 'resolve_configured_file_path', lambda store, path, **kw: (None, path, '/configured/Files/' + path))
    monkeypatch.setattr(owner, 'lakehouse_file_filesystem', lambda df, path, **kw: (fs, Path(path), Path))
    return SimpleNamespace(owner=owner, fs=fs, frame=frame, writer=writer)


@pytest.mark.parametrize('fmt', ['csv', 'parquet', 'json'])
@pytest.mark.parametrize('single', [False, True])
def test_foundation_layout_formats_and_metrics(output, fmt, single):
    result = write_lakehouse_file(output.frame, 'nested/orders.' + fmt, file_format=fmt,
                                  single_file=single, write_options={'header': True})
    assert result['resolved_path'] == '/configured/Files/nested/orders.' + fmt
    assert result['published'] and result['write_metrics']['output_bytes'] == 12
    assert result['write_metrics']['file_count'] == 1
    output.writer.format.assert_called_once_with(fmt)
    expected = {"header": True}
    if single:
        expected["maxRecordsPerFile"] = 0
        if fmt in {"csv", "json"}:
            expected["compression"] = "none"
    output.writer.options.assert_called_once_with(**expected)
    if single:
        output.frame.coalesce.assert_called_once_with(1)
        assert output.fs.renames and output.fs.deleted
        assert not any('.fabricops-' in key for key in output.fs.entries)
    else:
        output.frame.coalesce.assert_not_called()


@pytest.mark.parametrize('mode', ['overwrite', 'append', 'ignore', 'errorifexists'])
def test_dataset_collisions(output, mode):
    target = '/configured/Files/orders'
    output.fs.entries[target] = None
    if mode == 'errorifexists':
        with pytest.raises(FileExistsError):
            write_lakehouse_file(output.frame, 'orders', mode=mode)
    else:
        result = write_lakehouse_file(output.frame, 'orders', mode=mode)
        assert result['published'] == (mode != 'ignore')
        if mode != 'ignore':
            output.writer.mode.assert_called_once_with("errorifexists" if mode == "overwrite" else mode)
    if mode in {'ignore', 'errorifexists'}:
        output.writer.save.assert_not_called()


@pytest.mark.parametrize('mode', ['overwrite', 'ignore', 'errorifexists'])
def test_single_file_collisions(output, mode):
    output.fs.entries['/configured/Files/orders.csv'] = 8
    if mode == 'errorifexists':
        with pytest.raises(FileExistsError):
            write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', single_file=True, mode=mode)
    else:
        result = write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', single_file=True, mode=mode)
        assert result['published'] == (mode == 'overwrite')
        assert output.fs.entries['/configured/Files/orders.csv'] == (12 if mode == 'overwrite' else 8)
    assert not any('.fabricops-' in key for key in output.fs.entries)


@pytest.mark.parametrize('changes', [
    {'relative_path': '../escape'}, {'relative_path': '/absolute'}, {'relative_path': 'a//b'},
    {'relative_path': 'Files/orders.csv'}, {'relative_path': 'a/*.csv'}, {'relative_path': 'a/%2e'},
    {'relative_path': 'https://elsewhere'}, {'file_format': 'excel'}, {'file_format': 'xml'},
    {'write_options': {'path': 'elsewhere'}}, {'write_options': {'maxRecordsPerFile': 2}},
    {'single_file': True, 'mode': 'append'}, {'single_file': True, 'write_options': {'Compression': 'gzip'}}, {'single_file': True, 'relative_path': 'orders'},
    {'single_file': True, 'repartition_by': 2}, {'max_single_file_bytes': 0},
])
def test_invalid_foundation_requests(output, changes):
    args = dict(relative_path='orders.csv', file_format='csv')
    args.update(changes)
    with pytest.raises(ValueError):
        write_lakehouse_file(output.frame, **args)
    output.writer.save.assert_not_called()


def test_existing_physical_file_cannot_be_appended_as_dataset(output):
    output.fs.entries['/configured/Files/orders'] = 12
    with pytest.raises(ValueError, match='layout'):
        write_lakehouse_file(output.frame, 'orders', mode='append')
    output.writer.save.assert_not_called()


@pytest.mark.parametrize('limit', ['rows', 'bytes'])
def test_single_file_safeguards_preserve_existing(output, limit):
    output.fs.entries['/configured/Files/orders.csv'] = 8
    with pytest.raises(ValueError, match='limit exceeded'):
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', mode='overwrite', single_file=True,
            **({'max_single_file_rows': 1} if limit == 'rows' else {'max_single_file_bytes': 1}))
    assert output.fs.entries['/configured/Files/orders.csv'] == 8
    assert not output.fs.renames
    assert not any('.fabricops-' in key for key in output.fs.entries)


def test_empty_dataframe_and_repartition(output):
    output.frame.limit.return_value.count.return_value = 0
    assert write_lakehouse_file(output.frame, 'empty.csv', file_format='csv', single_file=True)['published']
    write_lakehouse_file(output.frame, 'parallel', repartition_by=(4, 'id'))
    output.frame.repartition.assert_called_once_with(4, 'id')


def test_shortcut_error_and_cleanup(output):
    output.writer.save.side_effect = PermissionError('read-only shortcut')
    with pytest.raises(RuntimeError, match='shortcut'):
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', single_file=True)
    assert output.fs.deleted
    assert not output.fs.renames


@pytest.mark.parametrize('fmt', ['csv', 'parquet', 'json'])
@pytest.mark.parametrize('mode', ['Dry Run', 'Ungoverned'])
def test_orchestrated_files_track_sources_and_do_not_finalize(files, monkeypatch, fmt, mode):
    io = importlib.import_module('fabricops_kit.io')
    writer = Mock(return_value={'resolved_path': 'physical/output', 'published': True,
        'publication_status': 'published', 'write_metrics': {'file_count': 1, 'output_bytes': 12, 'rows_committed': None}})
    monkeypatch.setattr(io, 'write_lakehouse_file', writer)
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'completed', 'row_count': 2})
    session = setup_pipeline(pipeline_mode=mode)
    source = orchestrate_read(store='Bronze', relative_path='input/orders.csv', file_format='csv')
    result = orchestrate_write(files.runtime.frame, store='Silver', relative_path='nested/orders.' + fmt,
        file_format=fmt, write_mode='overwrite', write_options={'header': True})
    assert result['published'] == (mode == 'Ungoverned')
    assert result['source_id'] != source['source_id'] and 'table_id' not in result
    assert result['source_ids'] == [source['source_id']]
    assert not session.closed and not session.plan.evidence['sealed']
    if mode == 'Dry Run':
        writer.assert_not_called()
    else:
        assert result['publication_status'] == 'published'
        assert writer.call_args.kwargs['write_options'] == {'header': True}
    run = finalize_pipeline(session)
    shared.validate_pipeline_run(run)
    target = next(op for op in run['operations'] if op['pipeline_role'] == 'target')
    assert target['table_id'] is None and target['source_id'] == result['source_id']
    assert target['output_path'] == result['resolved_path']
    assert target['file_write_parameters_json']


@pytest.mark.parametrize('changes', [{'schema': 'demo'}, {'table_name': 'orders'}, {'file_format': None},
    {'write_mode': 'scd1'}, {'write_mode': 'append_all'}, {'write_parameters': {}}, {'write_options': {'path': 'x'}}])
def test_invalid_orchestrated_file_destinations(files, changes):
    session = setup_pipeline(pipeline_mode='Dry Run')
    args = dict(store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    args.update(changes)
    with pytest.raises(ValueError):
        orchestrate_write(files.runtime.frame, **args)
    assert session.closed


def test_governed_file_target_rejected_before_planning(files, monkeypatch):
    session = setup_pipeline(pipeline_mode='Dry Run')
    from dataclasses import replace
    session.plan = replace(session.plan, execution_mode='governed')
    monkeypatch.setattr(session, 'close', Mock())
    with pytest.raises(ValueError, match='explicit destination authorization'):
        orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    assert not session.plan.evidence['operations']
    session.plan = replace(session.plan, execution_mode='dry_run')


def test_foundation_resolves_configured_store(output, monkeypatch):
    from tests.helpers import framework_config
    routing = importlib.import_module('fabricops_kit.io.shared')
    monkeypatch.setattr(output.owner, 'resolve_configured_file_path', routing.resolve_configured_file_path)
    config = framework_config()
    context = {'config': config, 'scope_workspace_id': 'dev'}
    result = write_lakehouse_file(output.frame, 'nested/orders.csv', store='Silver', file_format='csv', context=context)
    assert result['resolved_path'] == config.path_config.paths['dev']['Silver'].root + '/Files/nested/orders.csv'
    with pytest.raises(ValueError, match='lakehouse'):
        write_lakehouse_file(output.frame, 'orders.csv', store='Gold', context=context)


@pytest.mark.parametrize('protected_path', ['nested/orders.csv', 'nested', 'nested/*.csv', '*'])
def test_ungoverned_file_protection_ignores_format_and_options(monkeypatch, protected_path):
    import json
    from fabricops_kit.data_contract.shared import file_source_identity
    activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    protected = file_source_identity(workspace_id='workspace', item_id='item', relative_path=protected_path,
        file_format='json', reader_options={'multiLine': True})
    destination = file_source_identity(workspace_id='workspace', item_id='item', relative_path='nested/orders.csv', file_format='csv')
    monkeypatch.setattr(activation, 'read_activations', lambda **kw: [{'workspace_id': 'workspace',
        'table_id': None, 'destination_json': json.dumps(protected)}])
    with pytest.raises(ValueError, match='protected file'):
        activation.guard_ungoverned_write(SimpleNamespace(runtime_context={}), destination['source_id'], destination)


def test_source_guardrail_blocks_file_publication(files, monkeypatch):
    monkeypatch.setattr(files.runtime.write, 'source_guardrail_results', lambda *a: [{'can_continue': False}])
    session = setup_pipeline(pipeline_mode='Ungoverned')
    writer = Mock()
    monkeypatch.setattr(importlib.import_module('fabricops_kit.io'), 'write_lakehouse_file', writer)
    with pytest.raises(ValueError, match='Source Guardrails'):
        orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    writer.assert_not_called()
    assert session.closed


def test_profiling_failure_retains_published_file_status(files, monkeypatch):
    io = importlib.import_module('fabricops_kit.io')
    monkeypatch.setattr(io, 'write_lakehouse_file', Mock(return_value={'published': True, 'publication_status': 'published',
        'resolved_path': 'physical/output', 'write_metrics': {'file_count': 1}}))
    monkeypatch.setattr(shared, 'schedule_file_profiling', Mock(side_effect=RuntimeError('profile failed')))
    session = setup_pipeline(pipeline_mode='Ungoverned')
    with pytest.raises(RuntimeError) as caught:
        orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='append')
    assert caught.value.published is True
    record = next(iter(session.plan.evidence['operations'].values()))
    assert record['publication_status'] == 'published' and record['status'] == 'failed'
    assert record['metrics']['file_count'] == 1


def test_cleanup_failure_reports_successful_publication(output):
    output.fs.delete = Mock(return_value=False)
    with pytest.raises(RuntimeError, match="publication completed") as caught:
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', single_file=True)
    assert caught.value.published is True
    assert output.fs.entries['/configured/Files/orders.csv'] == 12


def test_dry_run_reports_blocked_sources_without_publication(files, monkeypatch):
    monkeypatch.setattr(files.runtime.write, 'source_guardrail_results', lambda *a: [{'can_continue': False}])
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'disabled'})
    setup_pipeline(pipeline_mode='Dry Run')
    result = orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    assert result['validation_passed'] is False and result['published'] is False
    assert result['testing_completed_at'] and result['output_layout'] == 'dataset_folder'


@pytest.mark.parametrize('fmt', ['csv', 'parquet', 'json'])
def test_orchestrated_single_artifact_uses_real_foundation(files, output, monkeypatch, fmt):
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'disabled'})
    session = setup_pipeline(pipeline_mode='Ungoverned')
    result = orchestrate_write(output.frame, store='Silver', relative_path='orders.' + fmt,
        file_format=fmt, single_file=True, write_mode='overwrite')
    assert result['published'] is True and result['output_layout'] == 'single_file'
    output.frame.coalesce.assert_called_once_with(1)
    target = next(iter(session.plan.evidence['operations'].values()))
    assert target['publication_status'] == 'published'
    assert target['output_path'] == result['resolved_path']


@pytest.mark.parametrize('single', [False, True])
@pytest.mark.parametrize('failure', ['backup', 'publication', 'rollback', 'after_publication'])
def test_overwrite_failures_preserve_recoverable_output(output, single, failure):
    target = '/configured/Files/orders.csv'
    output.fs.entries[target] = 8 if single else None
    old_part = target if single else target + '/part-old.csv'
    output.fs.entries[old_part] = 8
    rename = output.fs.rename
    calls = 0
    def faulty_rename(source, destination):
        nonlocal calls
        calls += 1
        if failure == 'backup' and calls == 1:
            return False
        if failure in {'publication', 'rollback'} and calls == 2:
            return False
        if failure == 'rollback' and calls == 3:
            return False
        result = rename(source, destination)
        if failure == 'after_publication' and calls == 2:
            raise OSError('publication acknowledgement lost')
        return result
    output.fs.rename = faulty_rename
    with pytest.raises(RuntimeError) as caught:
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', single_file=single, mode='overwrite')
    assert caught.value.recovery_paths
    if failure in {'backup', 'publication'}:
        assert output.fs.entries[old_part] == 8
    else:
        assert any('.fabricops-backup-' in key and value == 8 for key, value in output.fs.entries.items())
    assert 12 in output.fs.entries.values()  # Replacement survives in staging or at the target.
    assert not output.fs.deleted


@pytest.mark.parametrize('single', [False, True])
def test_overwrite_staging_failure_leaves_original_untouched(output, single):
    target = '/configured/Files/orders.csv'
    output.fs.entries[target] = 8 if single else None
    output.writer.save.side_effect = OSError('staging failed')
    with pytest.raises(RuntimeError):
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', single_file=single, mode='overwrite')
    assert output.fs.entries[target] == (8 if single else None)
    assert not output.fs.renames


def test_backup_cleanup_failure_retains_publication_and_recovery_in_run(files, output, monkeypatch):
    output.fs.entries['/configured/Files/orders.csv'] = 8
    delete = output.fs.delete
    output.fs.delete = lambda path, recursive: False if '.fabricops-backup-' in str(path) else delete(path, recursive)
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'disabled'})
    session = setup_pipeline(pipeline_mode='Ungoverned')
    with pytest.raises(RuntimeError) as caught:
        orchestrate_write(output.frame, store='Silver', relative_path='orders.csv', file_format='csv',
            single_file=True, write_mode='overwrite')
    assert caught.value.published is True and caught.value.recovery_paths
    assert output.fs.entries['/configured/Files/orders.csv'] == 12
    assert any('.fabricops-backup-' in key and value == 8 for key, value in output.fs.entries.items())
    operation = next(iter(session.plan.evidence['operations'].values()))
    assert operation['status'] == 'failed' and operation['publication_status'] == 'published'
    assert operation['output_path'] == '/configured/Files/orders.csv'



def test_overwrite_profile_failure_does_not_publish(files, monkeypatch):
    io = importlib.import_module('fabricops_kit.io')
    writer = Mock()
    monkeypatch.setattr(io, 'write_lakehouse_file', writer)
    monkeypatch.setattr(shared, 'schedule_file_profiling', Mock(side_effect=RuntimeError('profile failed')))
    setup_pipeline(pipeline_mode='Ungoverned')
    with pytest.raises(RuntimeError) as caught:
        orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    assert caught.value.published is False
    writer.assert_not_called()
