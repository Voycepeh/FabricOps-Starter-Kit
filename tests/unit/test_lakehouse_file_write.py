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
    frame.schema = SimpleNamespace(fields=[SimpleNamespace(name='id', dataType=SimpleNamespace(simpleString=lambda: 'bigint'))])
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
    def limits(rows=1_000_000, encoded_bytes=100_000_000):
        monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_ROWS', rows)
        monkeypatch.setattr(owner, '_MAX_SINGLE_FILE_BYTES', encoded_bytes)
    return SimpleNamespace(owner=owner, fs=fs, frame=frame, writer=writer, limits=limits)


@pytest.mark.parametrize('fmt', ['csv', 'json', 'parquet'])
@pytest.mark.parametrize('layout', ['default', 'row_limit', 'byte_limit', 'append_all'])
def test_formats_layout_policy_and_metrics(output, fmt, layout):
    if layout == 'row_limit':
        output.limits(rows=1)
    elif layout == 'byte_limit':
        output.limits(encoded_bytes=1)
    single = layout == 'default'
    result = write_lakehouse_file(output.frame, 'nested/orders.' + fmt, file_format=fmt,
        mode='append_all' if layout == 'append_all' else 'overwrite', write_options={'header': True})
    assert result['resolved_path'] == '/configured/Files/nested/orders.' + fmt
    assert result['relative_path'] == 'nested/orders.' + fmt
    assert result['published'] and result['publication_status'] == 'published'
    assert result['write_metrics']['output_bytes'] == result['output_bytes'] == 12
    assert result['write_metrics']['file_count'] == result['file_count'] == 1
    assert result['output_layout'] == ('single_file' if single else 'dataset_folder')
    assert result['overflow_reason'] == (layout if layout in {'row_limit', 'byte_limit'} else None)
    assert result['overflow_occurred'] is (layout in {'row_limit', 'byte_limit'})
    assert output.writer.save.call_count == (2 if layout == 'byte_limit' else 1)
    if layout in {'default', 'byte_limit'}:
        output.frame.coalesce.assert_called_once_with(1)
    else:
        output.frame.coalesce.assert_not_called()
    if layout == 'append_all':
        output.frame.limit.assert_not_called()
        output.writer.mode.assert_called_once_with('append')
    else:
        output.frame.limit.assert_called_once_with(2 if layout == 'row_limit' else 1_000_001)
    assert not any('.fabricops-' in key or '_parts' in key for key in output.fs.entries)


def test_internal_policy_and_public_signatures(output):
    import inspect
    assert output.owner._MAX_SINGLE_FILE_ROWS == 1_000_000
    assert output.owner._MAX_SINGLE_FILE_BYTES == 100_000_000
    removed = {'single_file', 'max_single_file_rows', 'max_single_file_bytes'}
    for function in (write_lakehouse_file, orchestrate_write):
        assert removed.isdisjoint(inspect.signature(function).parameters)


@pytest.mark.parametrize('name,value', [('single_file', False), ('max_single_file_rows', 1), ('max_single_file_bytes', 1)])
def test_removed_keywords_have_no_compatibility_shims(output, name, value):
    with pytest.raises(TypeError, match=name):
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', **{name: value})
    with pytest.raises(TypeError, match=name):
        orchestrate_write(output.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite', **{name: value})
    output.writer.save.assert_not_called()


@pytest.mark.parametrize('changes', [
    {'relative_path': '../escape'}, {'relative_path': '/absolute'}, {'relative_path': 'a//b'},
    {'relative_path': 'Files/orders.csv'}, {'relative_path': 'a/*.csv'}, {'relative_path': 'a/%2e'},
    {'relative_path': 'https://elsewhere'}, {'file_format': 'excel'}, {'file_format': 'xml'},
    {'write_options': {'path': 'elsewhere'}}, {'write_options': {'maxRecordsPerFile': 2}},
    {'write_options': {'mode': 'append'}}, {'write_options': {'partitionBy': 'id'}},
    {'mode': 'errorifexists'}, {'mode': 'ignore'}, {'mode': 'append'}, {'mode': None},
    {'write_options': {'Compression': 'gzip'}}, {'relative_path': 'orders'},
    {'write_options': []}, {'write_options': {'': 'x'}}, {'file_format': 'json', 'write_options': {'lineSep': '|'}},
])
def test_invalid_requests_fail_before_mutation(output, changes):
    args = dict(relative_path='orders.csv', file_format='csv')
    args.update(changes)
    with pytest.raises(ValueError):
        write_lakehouse_file(output.frame, **args)
    output.writer.save.assert_not_called()
    assert not output.fs.deleted and not output.fs.renames


@pytest.mark.parametrize('rows,encoded_bytes', [(2, 12), (3, 13)])
def test_single_file_limits_are_inclusive(output, rows, encoded_bytes):
    output.limits(rows, encoded_bytes)
    result = write_lakehouse_file(output.frame, 'orders.csv', file_format='csv')
    assert result['output_layout'] == 'single_file' and not result['overflow_occurred']


@pytest.mark.parametrize('layout', ['default', 'row_limit', 'byte_limit'])
def test_repartitioning_is_applied_before_single_or_distributed_staging(output, layout):
    if layout == 'row_limit':
        output.limits(rows=1)
    elif layout == 'byte_limit':
        output.limits(encoded_bytes=1)
    write_lakehouse_file(output.frame, 'orders.csv', file_format='csv', repartition_by=(4, 'id'))
    output.frame.repartition.assert_called_once_with(4, 'id')
    if layout == 'row_limit':
        output.frame.coalesce.assert_not_called()
    else:
        output.frame.coalesce.assert_called_once_with(1)
    last_options = output.writer.options.call_args.kwargs
    assert ('maxRecordsPerFile' in last_options) is (layout == 'default')


def test_append_all_requires_dataset_and_allows_compression(output):
    target = '/configured/Files/orders'
    output.fs.entries[target] = 8
    with pytest.raises(ValueError, match='dataset folder'):
        write_lakehouse_file(output.frame, 'orders', file_format='csv', mode='append_all')
    output.writer.save.assert_not_called()
    assert not output.fs.renames and not output.fs.deleted
    output.fs.entries[target] = None
    result = write_lakehouse_file(output.frame, 'orders', file_format='csv', mode='append_all',
        write_options={'compression': 'gzip'}, repartition_by=4)
    assert result['output_layout'] == 'dataset_folder' and result['overflow_reason'] is None
    output.writer.options.assert_called_once_with(compression='gzip')
    output.frame.repartition.assert_called_once_with(4)


def test_empty_frame_uses_native_single_artifact(output):
    output.frame.limit.return_value.count.return_value = 0
    result = write_lakehouse_file(output.frame, 'empty.csv', file_format='csv')
    assert result['published'] and result['output_layout'] == 'single_file'


@pytest.mark.parametrize('old_single', [False, True])
@pytest.mark.parametrize('new_single', [False, True])
def test_overwrite_changes_layout_and_cleans_old_backup(output, old_single, new_single):
    target = '/configured/Files/orders.csv'
    output.fs.entries[target] = 8 if old_single else None
    if not old_single:
        output.fs.entries[target + '/part-old.csv'] = 8
    if not new_single:
        output.limits(rows=1)
    delete = output.fs.delete
    def check_recursive(path, recursive):
        if '.fabricops-backup-' in str(path):
            assert recursive is (not old_single)
        return delete(path, recursive)
    output.fs.delete = check_recursive
    result = write_lakehouse_file(output.frame, 'orders.csv', file_format='csv')
    assert result['output_layout'] == ('single_file' if new_single else 'dataset_folder')
    assert output.fs.isFile(Path(target)) is new_single
    assert not any('.fabricops-' in key for key in output.fs.entries)


@pytest.mark.parametrize('old_single', [False, True])
@pytest.mark.parametrize('limit', ['default', 'row_limit', 'byte_limit'])
@pytest.mark.parametrize('failure', ['staging', 'backup', 'publication', 'rollback', 'after_publication'])
def test_failures_preserve_existing_destination_or_recovery(output, old_single, limit, failure):
    target = '/configured/Files/orders.csv'
    old_part = target if old_single else target + '/part-old.csv'
    output.fs.entries[target] = 8 if old_single else None
    output.fs.entries[old_part] = 8
    if limit == 'row_limit':
        output.limits(rows=1)
    elif limit == 'byte_limit':
        output.limits(encoded_bytes=1)
    save = output.writer.save.side_effect
    def fail_staging(path):
        if limit != 'byte_limit' or output.writer.save.call_count == 2:
            raise PermissionError('staging refused')
        save(path)
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
    if failure == 'staging':
        output.writer.save.side_effect = fail_staging
    else:
        output.fs.rename = faulty_rename
    with pytest.raises(RuntimeError) as caught:
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv')
    if failure in {'staging', 'backup', 'publication'}:
        assert output.fs.entries[old_part] == 8
    else:
        assert any('.fabricops-backup-' in key and value == 8 for key, value in output.fs.entries.items())
    if failure == 'staging':
        assert not output.fs.renames
    else:
        assert caught.value.recovery_paths
        assert 12 in output.fs.entries.values()
        # Byte overflow staging is discarded before publication. Recovery staging is retained.
        assert all('.fabricops-backup-' not in path for path in output.fs.deleted)


@pytest.mark.parametrize('error', [PermissionError('permission denied'), OSError('filesystem failure'), RuntimeError('executor out of memory')])
def test_unrelated_failures_never_trigger_overflow(output, error):
    output.writer.save.side_effect = error
    with pytest.raises(RuntimeError) as caught:
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv')
    assert caught.value.__cause__ is error and caught.value.overflow_occurred is False
    assert output.writer.save.call_count == 1 and not output.fs.renames


def test_oversized_staging_cleanup_failure_never_starts_distributed_write(output):
    output.limits(encoded_bytes=1)
    output.fs.entries['/configured/Files/orders.csv'] = 8
    output.fs.delete = Mock(return_value=False)
    with pytest.raises(RuntimeError) as caught:
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv')
    assert output.writer.save.call_count == 1 and caught.value.recovery_paths
    assert output.fs.entries['/configured/Files/orders.csv'] == 8 and not output.fs.renames


def test_temporary_cleanup_failure_reports_completed_publication(output):
    output.fs.delete = Mock(return_value=False)
    with pytest.raises(RuntimeError, match='publication completed') as caught:
        write_lakehouse_file(output.frame, 'orders.csv', file_format='csv')
    assert caught.value.published and caught.value.recovery_paths
    assert caught.value.output_layout == 'single_file'


@pytest.mark.parametrize('mode', ['Dry Run', 'Ungoverned'])
@pytest.mark.parametrize('layout', ['default', 'row_limit', 'byte_limit', 'append_all'])
@pytest.mark.parametrize('fmt', ['csv', 'json', 'parquet'])
def test_orchestration_retains_actual_layout_and_sources(files, output, monkeypatch, mode, layout, fmt):
    import json
    if layout == 'row_limit':
        output.limits(rows=1)
    elif layout == 'byte_limit':
        output.limits(encoded_bytes=1)
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'completed', 'row_count': 2})
    session = setup_pipeline(pipeline_mode=mode)
    source = orchestrate_read(store='Bronze', relative_path='input/orders.csv', file_format='csv')
    result = orchestrate_write(output.frame, store='Silver', relative_path='nested/orders.' + fmt, file_format=fmt,
        write_mode='append_all' if layout == 'append_all' else 'overwrite', repartition_by=4)
    record = next(row for row in session.plan.evidence['operations'].values() if row.get('write_mode'))
    outcome = json.loads(record['file_write_parameters_json'])
    assert result['resolved_path'] == record['output_path']
    assert result['source_assets'] == [{'table_id': source['table_id'], 'asset_type': 'FILE'}]
    assert not session.closed
    if mode == 'Dry Run':
        assert result['output_layout'] is result['overflow_occurred'] is result['overflow_reason'] is None
        assert result['publication_status'] == 'not_published'
        output.writer.save.assert_not_called()
    else:
        assert result['published'] and result['publication_status'] == 'published'
        assert result['output_layout'] == outcome['output_layout'] == ('single_file' if layout == 'default' else 'dataset_folder')
        assert result['overflow_reason'] == outcome['overflow_reason'] == (layout if layout in {'row_limit', 'byte_limit'} else None)
        assert result['write_metrics']['file_count'] == 1
        assert {'single_file', 'max_single_file_rows', 'max_single_file_bytes'}.isdisjoint(outcome)
    shared.validate_pipeline_run(finalize_pipeline(session))


@pytest.mark.parametrize('changes', [{'schema': 'demo'}, {'table_name': 'orders'}, {'file_format': None},
    {'write_mode': 'scd1'}, {'write_mode': 'append_new_only'}, {'write_mode': 'append'}, {'write_mode': 'ignore'},
    {'write_mode': 'errorifexists'}, {'write_parameters': {}}, {'write_options': {'path': 'x'}}])
def test_invalid_orchestrated_destinations(files, changes):
    session = setup_pipeline(pipeline_mode='Dry Run')
    args = dict(store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    args.update(changes)
    with pytest.raises(ValueError):
        orchestrate_write(files.runtime.frame, **args)
    assert session.closed


@pytest.mark.parametrize('layout', ['default', 'row_limit', 'byte_limit'])
def test_backup_cleanup_failure_retains_published_outcome_in_run(files, output, monkeypatch, layout):
    import json
    if layout == 'row_limit':
        output.limits(rows=1)
    elif layout == 'byte_limit':
        output.limits(encoded_bytes=1)
    output.fs.entries['/configured/Files/orders.csv'] = 8
    delete = output.fs.delete
    output.fs.delete = lambda path, recursive: False if '.fabricops-backup-' in str(path) else delete(path, recursive)
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'disabled'})
    session = setup_pipeline(pipeline_mode='Ungoverned')
    with pytest.raises(RuntimeError) as caught:
        orchestrate_write(output.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    assert caught.value.published is True and caught.value.recovery_paths
    record = next(iter(session.plan.evidence['operations'].values()))
    outcome = json.loads(record['file_write_parameters_json'])
    assert record['publication_status'] == 'published' and record['status'] == 'failed'
    assert outcome['output_layout'] == ('single_file' if layout == 'default' else 'dataset_folder')
    assert outcome['overflow_reason'] == (None if layout == 'default' else layout)


def test_overwrite_profiles_lazy_source_before_publication(files, monkeypatch):
    io = importlib.import_module('fabricops_kit.io')
    writer = Mock()
    monkeypatch.setattr(io, 'write_lakehouse_file', writer)
    monkeypatch.setattr(shared, 'schedule_file_profiling', Mock(side_effect=RuntimeError('profile failed')))
    setup_pipeline(pipeline_mode='Ungoverned')
    with pytest.raises(RuntimeError) as caught:
        orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    assert caught.value.published is False
    writer.assert_not_called()


def test_append_all_accepts_extensionless_path(files, output, monkeypatch):
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'disabled'})
    session = setup_pipeline(pipeline_mode='Ungoverned')
    result = orchestrate_write(output.frame, store='Silver', relative_path='orders', file_format='csv', write_mode='append_all')
    assert result['published'] and result['output_layout'] == 'dataset_folder'
    shared.validate_pipeline_run(finalize_pipeline(session))


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
        write_lakehouse_file(output.frame, 'orders.parquet', store='Gold', context=context)



@pytest.mark.parametrize('protected_path', ['nested/orders.csv', 'nested', 'nested/*.csv', '*'])
def test_ungoverned_file_protection_ignores_format_and_options(monkeypatch, protected_path):
    import json
    from fabricops_kit.data_contract.shared import file_source_identity
    activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    protected = file_source_identity(asset_workspace_id='workspace', item_id='item', relative_path=protected_path,
        file_format='json', reader_options={'multiLine': True})
    destination = file_source_identity(asset_workspace_id='workspace', item_id='item', relative_path='nested/orders.csv', file_format='csv')
    monkeypatch.setattr(activation, 'read_activations', lambda **kw: [{'asset_workspace_id': 'workspace',
        'destination_json': json.dumps(protected)}])
    with pytest.raises(ValueError, match='protected file'):
        activation.guard_ungoverned_write(SimpleNamespace(runtime_context={}), destination['table_id'], destination)



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
        orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='append_all')
    assert caught.value.published is True
    record = next(iter(session.plan.evidence['operations'].values()))
    assert record['publication_status'] == 'published' and record['status'] == 'failed'
    assert record['metrics']['file_count'] == 1



def test_dry_run_reports_blocked_sources_without_publication(files, monkeypatch):
    monkeypatch.setattr(files.runtime.write, 'source_guardrail_results', lambda *a: [{'can_continue': False}])
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'status': 'disabled'})
    setup_pipeline(pipeline_mode='Dry Run')
    result = orchestrate_write(files.runtime.frame, store='Silver', relative_path='orders.csv', file_format='csv', write_mode='overwrite')
    assert result['validation_passed'] is False and result['published'] is False
    assert result['testing_completed_at'] and result['output_layout'] is None
    assert result['overflow_occurred'] is None
