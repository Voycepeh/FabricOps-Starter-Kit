"""Retired Preview inventory and advisory setup behavior."""

from tests.helpers import call_with_spark

from dataclasses import replace
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    RETIRED_PREVIEW_METADATA_TABLES,
    metadata_table_schema_registry,
)
from tests.helpers import framework_config


def test_retirement_inventory_matches_released_lifecycle():
    """Every released table removed from canonical source needs an explicit declaration."""
    inventories = [yaml.safe_load(path.read_text()) for path in Path('docs/releases/manifests').glob('*.yml')]
    released = {item['name'] for manifest in inventories for item in manifest['metadata_tables']}
    retired = RETIRED_PREVIEW_METADATA_TABLES
    assert {name for name, declaration in retired.items() if not declaration.get("unreleased")} == released - set(CANONICAL_METADATA_TABLES)
    assert {name for name, declaration in retired.items() if declaration.get("unreleased")} == {"METADATA_ACTIVATION_STATE"}
    for name in ('METADATA_ENRICHMENT', 'METADATA_GUARDRAIL', 'METADATA_SOURCE_OBSERVATION'):
        assert retired[name]['retired_in'] == '0.3.0'
    for manifest in inventories:
        for item in manifest['metadata_tables']:
            name = item['name']
            if item['status'] == 'live':
                assert name in CANONICAL_METADATA_TABLES
                assert name not in retired
            if name not in retired:
                continue
            declaration = retired[name]
            assert declaration['guidance']
            if item['status'] == 'discontinued':
                assert declaration['retired_in'] == item['discontinued_in']
            else:
                assert item['status'] == 'preview'
                assert tuple(map(int, declaration['retired_in'].split('.'))) > tuple(map(int, manifest['release_version'].split('.')))


@pytest.mark.parametrize('canonical_exists', [False, True])
@pytest.mark.parametrize('presence', ['missing', 'present', 'denied', 'storage'])
@pytest.mark.parametrize('verbose', [False, True])
def test_retirement_alerts_are_presence_only_and_nonblocking(monkeypatch, capsys, canonical_exists, presence, verbose):
    """Probe both configured schemas, preserve canonical data and honor quiet output."""
    setup = import_module('fabricops_kit.config.setup_metadata_tables')
    registry = metadata_table_schema_registry()
    cfg = replace(framework_config(), governance_metadata_schema='custom_gov', engineering_metadata_schema='custom_eng')
    routes, writes = [], []
    tables = dict(registry) if canonical_exists else {}
    monkeypatch.setattr('fabricops_kit.config.audit.build_runtime_audit_fields', lambda **kw: {})

    class Frame:
        def __init__(self, schema):
            self.schema = schema

        def where(self, _expr): return self
        def limit(self, _value): return self
        def take(self, _value): return []
        def select(self, *_columns): return self
        def toLocalIterator(self): return iter(())  # noqa: N802

    class HistoricalFrame:
        def __getattr__(self, name):
            raise AssertionError(f'Retired table must not be evaluated: {name}')

    def read(name, **kw):
        assert kw['store'] == 'Metadata'
        assert kw['context']['config'].path_config == cfg.path_config
        if not kw['context'].get('_fabricops_suppress_io_log'):
            print('underlying I/O')
        if name in RETIRED_PREVIEW_METADATA_TABLES:
            routes.append((kw['schema'], name))
            if presence == 'present':
                return HistoricalFrame()
            if presence == 'denied':
                raise PermissionError('credential not found; access denied')
            if presence == 'storage':
                raise OSError('storage endpoint not found')
        elif name in tables:
            return Frame(tables[name])
        raise RuntimeError('[TABLE_OR_VIEW_NOT_FOUND] Table does not exist')

    def write(frame, name, **kw):
        assert name in registry
        writes.append(name)
        tables[name] = frame.schema

    monkeypatch.setattr(setup, 'read_lakehouse_table', read)
    monkeypatch.setattr(setup, 'write_lakehouse_table', write)
    result = call_with_spark(SimpleNamespace(createDataFrame=lambda rows, schema: Frame(schema)), setup.setup_metadata_tables,
        config=cfg, env='dev', verbose=verbose, raise_on_failure=True,
    )
    assert result['status'] == 'ready'
    assert result['failed_tables'] == []
    assert set(routes) == {(schema, name) for schema in ('custom_gov', 'custom_eng') for name in RETIRED_PREVIEW_METADATA_TABLES}
    assert len(routes) == 2 * len(RETIRED_PREVIEW_METADATA_TABLES)
    assert writes == ([] if canonical_exists else list(registry))
    warnings = result['warnings']
    assert len(warnings) == (0 if presence == 'missing' else len(routes))
    for (schema, name), warning in zip(routes, warnings):
        assert f'{schema}.{name}' in warning
        if presence == 'present':
            assert f"v{RETIRED_PREVIEW_METADATA_TABLES[name]['retired_in']}" in warning
            assert 'no longer supported' in warning
            assert RETIRED_PREVIEW_METADATA_TABLES[name]['guidance'] in warning
            assert 'Preserve required definitions, progress or history' in warning
        else:
            assert 'presence is unknown' in warning
    output = capsys.readouterr().out
    if not verbose:
        assert output == ''
    else:
        assert 'underlying I/O' in output
        assert all(warning in output for warning in warnings)


@pytest.mark.parametrize('message', ['[PATH_NOT_FOUND] Path does not exist', '[DELTA_TABLE_NOT_FOUND] missing'])
def test_delta_absence_is_recognized(message):
    """Delta missing-path errors are distinct from generic storage failures."""
    setup = import_module('fabricops_kit.config.setup_metadata_tables')
    assert setup._retired_table_is_missing(RuntimeError(message))
    assert not setup._retired_table_is_missing(RuntimeError('credential not found'))
