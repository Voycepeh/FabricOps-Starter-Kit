"""Verify central metadata reads separate identical logical assets in multiple DEV workspaces."""
from importlib import import_module

import pytest

from fabricops_kit.config import shared as config
from tests.unit.test_workspace_registry import DEV, OTHER, LOCATOR, registration

pytestmark = pytest.mark.spark


@pytest.mark.parametrize('table', ['METADATA_DATA_CATALOGUE', 'METADATA_PIPELINE_RUN', 'METADATA_SOURCE_OBSERVATION'])
def test_engineering_metadata_reads_use_registered_workspace_scope(spark_session, monkeypatch, table):
    """Same environment and logical IDs cannot leak observations or activation candidates across workspaces."""
    module = import_module('fabricops_kit.io.read_lakehouse_table')
    frame = spark_session.createDataFrame([(DEV, 'DEV', 'orders', 'first'),
                                          (OTHER, 'DEV', 'orders', 'second'),
                                          (None, 'DEV', 'orders', 'unmigrated')],
                                         'execution_workspace_id string, environment_name string, table_id string, value string')
    monkeypatch.setattr(module, 'read_delta_path', lambda *args, **kwargs: frame)
    monkeypatch.setattr(module, 'get_spark_session', lambda *args: spark_session)
    with config.suspend_governed_context():
        for workspace, expected in [(DEV, 'first'), (OTHER, 'second')]:
            context = config.registration_context(registration(workspace), locator=LOCATOR, identity={})
            rows = module.read_lakehouse_table(table, store='Metadata', context=context).collect()
            assert [row.value for row in rows] == [expected]


def test_independent_public_io_does_not_require_workspace_registration(spark_session, monkeypatch):
    """A direct business read can use an explicit FrameworkConfig without starting a lifecycle."""
    module = import_module('fabricops_kit.io.read_lakehouse_table')
    frame = spark_session.sql('SELECT 42 AS value')
    monkeypatch.setattr(module, 'read_delta_path', lambda *args, **kwargs: frame)
    monkeypatch.setattr(module, 'get_spark_session', lambda *args: spark_session)
    context = config.registration_context(registration(), locator=LOCATOR, identity={})
    with config.suspend_governed_context():
        assert module.read_lakehouse_table('orders', store='Bronze', schema='dbo', context=context).first().value == 42
