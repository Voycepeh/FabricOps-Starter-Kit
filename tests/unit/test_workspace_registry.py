"""Central registry, bootstrap, configuration locking and workspace isolation contracts."""
# ruff: noqa: D103
from copy import deepcopy
from dataclasses import asdict
from types import SimpleNamespace
from unittest.mock import Mock
import importlib
import json
import sys
from uuid import UUID

import pytest

from fabricops_kit.config import shared as config
from fabricops_kit.activated_pipeline import shared as activation

ORIGINAL_BOOTSTRAP = config.registry_bootstrap
ORIGINAL_READINESS = config.check_governed_readiness

GOV, META, DEV, OTHER, PROD, NOTEBOOK = [str(UUID(int=n)) for n in range(1, 7)]
LOCATOR = dict(governance_workspace_id=GOV, metadata_item_id=META,
               governance_schema='governance', engineering_schema='engineering')


def registration(workspace=DEV, environment='DEV', mode='Test'):
    return {'workspace_id': workspace, 'display_name': 'Arbitrary workspace label', 'environment': environment,
            'status': 'active', 'resources': {
                key: dict(workspace_id=GOV if key == 'Metadata' else workspace,
                          item_id=META if key == 'Metadata' else str(UUID(int=100 + n)),
                          kind='lakehouse', schema_enabled=True, schema='dbo')
                for n, key in enumerate(('Bronze', 'Silver', 'Gold', 'Metadata'))},
            'notebooks': {NOTEBOOK: dict(pipeline_id='stable-orders', mode=mode)}, 'settings': {}}


@pytest.fixture
def registry(monkeypatch):
    rows = {DEV: registration(), OTHER: registration(OTHER), PROD: registration(PROD, 'PROD', 'Live')}
    snapshot = {'format': 'fabricops.workspace-registry.v1', 'workspaces': rows}
    identity = {'currentWorkspaceId': DEV, 'currentNotebookId': NOTEBOOK, 'userName': 'engineer',
                'activityId': str(UUID(int=200))}
    monkeypatch.setitem(sys.modules, 'notebookutils', SimpleNamespace(runtime=SimpleNamespace(context=identity)))
    monkeypatch.setattr(config, 'check_governed_readiness', lambda *args, **kwargs: None)
    monkeypatch.setattr(config, 'registry_bootstrap', lambda: deepcopy(LOCATOR))
    monkeypatch.setattr(importlib.import_module('fabricops_kit.config.migrate_workspace_config'), 'registry_bootstrap', lambda: deepcopy(LOCATOR))
    monkeypatch.setattr(config, 'read_workspace_registry', lambda **kw: ('revision-one', deepcopy(snapshot)))
    spark = SimpleNamespace(conf=SimpleNamespace(set=Mock()))
    monkeypatch.setattr('fabricops_kit.io.shared.get_spark_session', lambda *args: spark)
    token = config._ACTIVE_GOVERNED_CONTEXT.set(None)
    yield SimpleNamespace(rows=rows, snapshot=snapshot, identity=identity, spark=spark)
    config._ACTIVE_GOVERNED_CONTEXT.reset(token)


@pytest.mark.parametrize('workspace,environment,mode', [(DEV, 'DEV', 'Test'), (PROD, 'PROD', 'Live')])
def test_runtime_workspace_selects_environment_metadata_and_notebook_binding(registry, workspace, environment, mode):
    registry.identity['currentWorkspaceId'] = workspace
    context = config.resolve_governed_workspace(require_pipeline=True)
    assert context['env'] == environment
    assert context['_registry_pipeline'] == dict(pipeline_id='stable-orders', mode=mode)
    assert context['notebook_name'] == NOTEBOOK  # no naming convention or display name required
    metadata = config.get_store(context['config'], environment, 'Metadata')
    assert (metadata.workspace_id, metadata.item_id) == (GOV, META)
    registry.spark.conf.set.assert_called_once_with('spark.sql.session.timeZone', 'UTC')


def test_multiple_workspaces_share_environment_but_have_independent_routes_and_approvals(registry):
    first = config.resolve_governed_workspace()
    registry.identity['currentWorkspaceId'] = OTHER
    second = config.resolve_governed_workspace()
    assert first['env'] == second['env'] == 'DEV'
    assert config.get_store(first['config'], 'DEV', 'Silver').workspace_id == DEV
    assert config.get_store(second['config'], 'DEV', 'Silver').workspace_id == OTHER
    state = json.loads(activation.empty_activation_state())
    activation.environment_activation(state, 'DEV', first)['pipelines']['orders'] = 'approved'
    assert activation.environment_activation(state, 'DEV', second)['pipelines'] == {}
    assert len(state['environments']) == 2


@pytest.mark.parametrize('inactive', [False, True])
def test_unknown_or_inactive_workspaces_fail_closed(registry, inactive):
    if inactive:
        registry.rows[DEV]['status'] = 'inactive'
    else:
        registry.rows.pop(DEV)
    with pytest.raises(PermissionError, match='unknown or inactive'):
        config.resolve_governed_workspace(require_pipeline=True)


def test_pipeline_requires_registered_runtime_notebook_id(registry):
    registry.rows[DEV]['notebooks'] = {}
    with pytest.raises(PermissionError, match='notebook ID'):
        config.resolve_governed_workspace(require_pipeline=True)
    assert config.resolve_governed_workspace()['env'] == 'DEV'  # standalone IO


def test_governed_context_rejects_env_resource_and_identity_overrides(registry):
    context = config.resolve_governed_workspace()
    for override in ({'env': 'PROD'}, {'config': {}}, {'workspace_id': PROD}, {'notebook_id': OTHER}):
        with pytest.raises(ValueError, match='cannot be overridden'):
            config.resolve_fabric_context(context=override)
    with pytest.raises(TypeError, match='immutable'):
        context['config'].path_config.paths['DEV']['Silver'] = context['config'].path_config.paths['DEV']['Gold']
    with pytest.raises(TypeError, match='immutable'):
        context['config'].governance_config.classification_levels.append('Unapproved')
    assert config.resolve_fabric_context(context={'activity_id': 'operation'})[1] == 'DEV'


@pytest.mark.parametrize('change', ['inactive', 'resource', 'runtime', 'binding'])
def test_operation_and_finalization_verifier_rejects_registration_or_runtime_drift(registry, change):
    context = config.resolve_governed_workspace(require_pipeline=True)
    config.verify_governed_context(context)
    if change == 'inactive': registry.rows[DEV]['status'] = 'inactive'
    if change == 'resource': registry.rows[DEV]['resources']['Silver']['item_id'] = OTHER
    if change == 'runtime': registry.identity['currentWorkspaceId'] = OTHER
    if change == 'binding': registry.rows[DEV]['notebooks'][NOTEBOOK]['mode'] = 'Live'
    with pytest.raises(RuntimeError, match='changed after'):
        config.verify_governed_context(context)


def test_unrelated_workspace_update_does_not_invalidate_pinned_registration(registry):
    context = config.resolve_governed_workspace()
    registry.rows[OTHER]['display_name'] = 'Renamed'
    config.verify_governed_context(context)


def test_cross_workspace_resources_are_explicit_and_central_metadata_cannot_move(registry):
    registry.rows[DEV]['resources']['Bronze']['workspace_id'] = OTHER
    context = config.resolve_governed_workspace()
    assert config.get_store(context['config'], 'DEV', 'Bronze').workspace_id == OTHER
    registry.rows[DEV]['resources']['Metadata']['item_id'] = OTHER
    with pytest.raises(ValueError, match='pinned central'):
        config.resolve_governed_workspace()


def test_governance_target_selection_requires_real_governance_workspace(registry):
    with pytest.raises(PermissionError, match='Only Governance'):
        config.resolve_governed_workspace(target_workspace_id=PROD)
    registry.identity['currentWorkspaceId'] = GOV
    context = config.resolve_governed_workspace(target_workspace_id=PROD)
    assert context['workspace_id'] == GOV and context['config'].execution_workspace_id == PROD


def test_zero_argument_setup_uses_central_binding_and_legacy_arguments_only_assert_it(registry, monkeypatch):
    module = importlib.import_module('fabricops_kit.pipeline.setup_pipeline')
    start = Mock(return_value='pipeline-session')
    monkeypatch.setattr('fabricops_kit.pipeline.shared.start_pipeline_session', start)
    assert module.setup_pipeline() == 'pipeline-session'
    assert start.call_args.args == ('stable-orders', 'Test')
    for kwargs in ({'pipeline_id': 'other'}, {'pipeline_mode': 'Live'}):
        with pytest.raises(ValueError, match='cannot override'):
            module.setup_pipeline(**kwargs)
    assert start.call_count == 1


def test_independent_public_io_accepts_explicit_framework_context_without_runtime(registry, monkeypatch):
    registry.identity.clear()
    context = config.registration_context(registration(), locator=LOCATOR, identity={})
    with config.suspend_governed_context():
        resolved, env, _ = config.resolve_fabric_context(context=context)
        assert env == 'DEV' and resolved == context['config']
        from fabricops_kit.io.shared import resolve_configured_lakehouse_table
        _store, table, schema, path = resolve_configured_lakehouse_table('Bronze', 'orders', 'sales', context=context)
        assert f'abfss://{DEV}@' in path and table == 'orders' and schema == 'sales'


def test_notebook_globals_cannot_supply_runtime_identity_or_default_context(registry, monkeypatch):
    import builtins
    monkeypatch.setattr(builtins, 'FABRIC_CONTEXT', {'config': {}, 'env': 'PROD', 'workspace_id': PROD}, raising=False)
    assert config.fabric_runtime_identity()['workspace_id'] == DEV
    with pytest.raises(RuntimeError, match='no longer supported'):
        config.get_default_fabric_context()
    registry.identity.clear()
    with pytest.raises(RuntimeError, match='valid workspace_id'):
        config.resolve_governed_workspace()


def test_migration_is_explicit_preserves_settings_and_does_not_publish(registry):
    from fabricops_kit import migrate_workspace_config
    old = config.registration_context(registration(), locator=LOCATOR, identity={})['config']
    assignments = [dict(legacy_environment='DEV', workspace_id=workspace, display_name='Team',
                        environment='DEV', status='inactive', notebooks={}) for workspace in (DEV, OTHER)]
    migrated = migrate_workspace_config(old, assignments=assignments)
    assert [row['workspace_id'] for row in migrated] == [DEV, OTHER]
    assert all(row['resources']['Metadata']['item_id'] == META for row in migrated)
    assert migrated[0]['settings']['governance_config'] == asdict(old.governance_config)
    assert registry.rows[DEV]['status'] == 'active'  # preview does not mutate registry


def test_bootstrap_ignores_environment_variables_and_missing_package_locator_fails(registry, monkeypatch):
    monkeypatch.setenv('FABRICOPS_REGISTRY_WORKSPACE_ID', PROD)
    monkeypatch.setenv('FABRICOPS_CONFIG', '{}')
    original = ORIGINAL_BOOTSTRAP
    with pytest.raises(RuntimeError, match='centrally published'):
        original()


def test_environment_labels_do_not_select_execution_mode_or_override_metadata_schema(registry):
    registry.rows[PROD]['notebooks'][NOTEBOOK]['mode'] = 'Test'
    registry.identity['currentWorkspaceId'] = PROD
    context = config.resolve_governed_workspace(require_pipeline=True)
    assert context["env"] == "PROD" and context["_registry_pipeline"]["mode"] == "Test"
    registry.identity['currentWorkspaceId'] = DEV
    registry.rows[DEV]['settings']['governance_metadata_schema'] = 'unapproved'
    with pytest.raises(ValueError, match='cannot override'):
        config.resolve_governed_workspace()


def test_warehouse_mapping_keeps_physical_name_independent_of_logical_gold(registry):
    registry.rows[DEV]['resources']['Gold'].update(kind='warehouse', item_name='CuratedWarehouse')
    context = config.resolve_governed_workspace()
    from fabricops_kit.io.shared import resolve_configured_warehouse_table
    store, schema, table, object_name = resolve_configured_warehouse_table('Gold', table_name='orders', schema='sales', context=context)
    assert object_name == 'CuratedWarehouse.sales.orders'
    assert store.workspace_id == DEV and store.key == 'Gold'


def test_zero_argument_pipeline_finalization_records_failure_and_incomplete_scope(registry, monkeypatch):
    import IPython
    from fabricops_kit import setup_pipeline, finalize_pipeline
    from fabricops_kit.pipeline import shared as pipeline
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    monkeypatch.setattr(pipeline, 'get_spark_session', lambda *args: registry.spark)
    rows = []
    monkeypatch.setattr(pipeline, '_merge_pipeline_run_row', lambda plan, row, **kwargs: rows.append(row))
    session = setup_pipeline()
    result = finalize_pipeline()
    assert result['status'] == 'incomplete' and rows[-1]['execution_workspace_id'] == DEV
    assert finalize_pipeline(session) == result
    session = setup_pipeline()
    result = finalize_pipeline(failed=True)
    assert result['status'] == 'failed' and rows[-1]['status'] == 'failed'
    assert rows[-1]['execution_workspace_id'] == DEV


def test_finalization_rejects_registry_drift_and_publishes_failed_test_run(registry, monkeypatch):
    import IPython
    from fabricops_kit import setup_pipeline, finalize_pipeline
    from fabricops_kit.pipeline import shared as pipeline
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    monkeypatch.setattr(pipeline, 'get_spark_session', lambda *args: registry.spark)
    rows = []
    monkeypatch.setattr(pipeline, '_merge_pipeline_run_row', lambda plan, row, **kwargs: rows.append(row))
    session = setup_pipeline()
    registry.rows[DEV]['status'] = 'inactive'
    with pytest.raises(RuntimeError, match='changed after setup'):
        finalize_pipeline(session)
    assert rows[-1]['status'] == 'failed' and session.closed



@pytest.mark.parametrize('environment', ['DEV', 'TEST', 'PROD'])
@pytest.mark.parametrize('mode', ['Test', 'Live'])
def test_execution_mode_is_explicit_registry_policy_for_every_environment(registry, environment, mode):
    registry.rows[DEV]['environment'] = environment
    registry.rows[DEV]['notebooks'][NOTEBOOK]['mode'] = mode
    resolved = config.resolve_governed_workspace(require_pipeline=True)
    assert resolved['env'] == environment
    assert resolved['_registry_pipeline']['mode'] == mode


@pytest.mark.parametrize('environment', ['DEV', 'TEST', 'PROD', 'canary-east'])
def test_activation_scope_is_based_on_identity_without_environment_specific_branches(environment):
    state = json.loads(activation.empty_activation_state())
    first = {'_registry_workspace_id': DEV}
    second = {'_registry_workspace_id': OTHER}
    activation.environment_activation(state, environment, first)['pipelines']['orders'] = 'approved'
    assert activation.environment_activation(state, environment, second)['pipelines'] == {}
    assert state['environments'][f'{environment}@{DEV}']['pipelines'] == {'orders': 'approved'}


def test_rejected_setup_assertion_keeps_existing_pipeline_open(registry, monkeypatch):
    import IPython
    from fabricops_kit import setup_pipeline
    from fabricops_kit.pipeline import shared as pipeline
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    monkeypatch.setattr(pipeline, 'get_spark_session', lambda *args: registry.spark)
    session = setup_pipeline()
    try:
        with pytest.raises(ValueError, match='cannot override'):
            setup_pipeline(pipeline_mode='Live')
        assert not session.closed and pipeline.current_pipeline_session() is session
    finally:
        session.close()


def test_governance_setup_requires_pipeline_finalization_first(registry, monkeypatch):
    import IPython
    from fabricops_kit import setup_pipeline, setup_governance
    from fabricops_kit.pipeline import shared as pipeline
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    monkeypatch.setattr(pipeline, 'get_spark_session', lambda *args: registry.spark)
    session = setup_pipeline()
    try:
        with pytest.raises(RuntimeError, match='Finalize the current pipeline'):
            setup_governance()
        assert not session.closed
    finally:
        session.close()


@pytest.mark.parametrize('failure', ['denied', 'outdated'])
def test_readiness_requires_readable_current_shared_metadata(registry, monkeypatch, failure):
    import fabricops_kit.io as io
    context = config.registration_context(registration(), locator=LOCATOR, identity={})
    if failure == 'denied':
        monkeypatch.setattr(io, 'read_lakehouse_table', Mock(side_effect=PermissionError('denied')))
    else:
        frame = SimpleNamespace(schema=SimpleNamespace(fieldNames=lambda: []))
        monkeypatch.setattr(io, 'read_lakehouse_table', lambda *args, **kwargs: frame)
    with pytest.raises(RuntimeError, match='Shared metadata readiness failed.*setup_metadata_tables'):
        ORIGINAL_READINESS(context, spark_session=registry.spark)


def test_bootstrap_uses_only_packaged_reviewed_locator(registry, monkeypatch):
    import importlib.resources
    monkeypatch.setenv('FABRICOPS_REGISTRY_WORKSPACE_ID', PROD)
    resource = SimpleNamespace(read_text=lambda: json.dumps(LOCATOR))
    monkeypatch.setattr(importlib.resources, 'files', lambda package: SimpleNamespace(joinpath=lambda name: resource))
    assert ORIGINAL_BOOTSTRAP() == LOCATOR


def test_register_workspace_enforces_governance_runtime_and_reviewed_token(registry, monkeypatch):
    module = importlib.import_module('fabricops_kit.config.register_workspace')
    monkeypatch.setattr(module, 'registry_bootstrap', lambda: LOCATOR)
    monkeypatch.setattr(module, 'read_workspace_registry', lambda **kwargs: ('reviewed', deepcopy(registry.snapshot)))
    writer = Mock(return_value='published')
    monkeypatch.setattr(module, 'commit_metadata_snapshot', writer)
    with pytest.raises(PermissionError, match='Governance Workspace'):
        module.register_workspace(registration(), expected_token='reviewed')
    registry.identity['currentWorkspaceId'] = GOV
    with pytest.raises(ValueError, match='changed'):
        module.register_workspace(registration(), expected_token='stale')
    assert module.register_workspace(registration(), expected_token='reviewed') == 'published'
    assert writer.call_count == 1
    assert writer.call_args.args[0] == config.REGISTRY_TABLE


def test_finalization_retains_approved_defaults_without_locking_independent_io(registry, monkeypatch):
    import IPython
    from fabricops_kit import setup_pipeline, finalize_pipeline
    from fabricops_kit.pipeline import shared as pipeline
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    monkeypatch.setattr(pipeline, 'get_spark_session', lambda *args: registry.spark)
    monkeypatch.setattr(pipeline, '_merge_pipeline_run_row', lambda *args, **kwargs: None)
    setup_pipeline()
    finalize_pipeline()
    assert config.resolve_fabric_context()[1] == 'DEV'
    independent = config.registration_context(registration(PROD, 'PROD'), locator=LOCATOR, identity={})
    resolved, env, context = config.resolve_fabric_context(context=independent)
    assert env == 'PROD' and resolved is independent['config']
    assert '_registry_revision' not in context
    assert not config.get_default_fabric_context().get('_registry_pipeline')


def test_registry_locator_cannot_change_during_an_execution(registry, monkeypatch):
    context = config.resolve_governed_workspace(require_pipeline=True)
    moved = {**LOCATOR, 'metadata_item_id': OTHER}
    monkeypatch.setattr(config, 'registry_bootstrap', lambda: moved)
    with pytest.raises(RuntimeError, match='bootstrap changed after setup'):
        config.verify_governed_context(context)


def test_frozen_configuration_round_trip_remains_immutable_for_spark_serialization(registry):
    import pickle
    from dataclasses import asdict
    original = config.resolve_governed_workspace(require_pipeline=True)['config']
    restored = pickle.loads(pickle.dumps(original))
    assert asdict(restored) == asdict(original)
    assert config.get_store(restored, 'DEV', 'Metadata').item_id == META
    with pytest.raises(TypeError, match='immutable'):
        restored.path_config.paths['DEV']['Gold'] = restored.path_config.paths['DEV']['Silver']
    with pytest.raises(TypeError, match='immutable'):
        restored.governance_config.classification_levels.append('Unapproved')
