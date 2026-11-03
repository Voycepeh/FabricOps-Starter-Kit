"""Real Delta Run migration preserves evidence, transactions and recovery."""
# ruff: noqa: F401, F811
from copy import deepcopy
import importlib
import json

import pytest

from fabricops_kit import finalize_pipeline
from fabricops_kit.activated_pipeline import shared as activation
from fabricops_kit.config.metadata_schemas import (
    decode_metadata_row, encode_metadata_row, metadata_json_schema, metadata_table_schema_registry,
)
from fabricops_kit.pipeline import shared
from tests.helpers import call_with_spark, framework_config
from tests.integration.test_pipeline_run_delta import runs_delta

pytestmark = pytest.mark.spark
RUN = 'METADATA_PIPELINE_RUN'
setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')


@pytest.fixture
def legacy_run(runs_delta, monkeypatch):
    """Seed exact retained native Run facts and route automatic setup to real Delta."""
    r = runs_delta
    plan = r.make()
    r.complete(plan)
    finalize_pipeline(shared.PipelineSession(plan, r.spark))
    approval = activation.tested_pipeline_run(testing_run_id=plan.plan_id,
        pipeline_name='Orders', pipeline_version='1', agreement_id='agreement', agreement_version='1',
        context=r.context, spark_session=r.spark)
    logical = r.rows()[0]
    native = metadata_table_schema_registry(logical=True)[RUN]
    registry = metadata_table_schema_registry()

    seed_version = 6

    def seed(native_columns=('operations', 'profiling', 'failures'), rows=None):
        nonlocal seed_version
        seed_version += 1
        from pyspark.sql.types import StructField, StructType
        schema = StructType([StructField(f.name, native[f.name].dataType if f.name in native_columns else f.dataType,
                                         f.nullable, f.metadata) for f in registry[RUN].fields])
        values = []
        for row in rows or [logical]:
            physical = encode_metadata_row(RUN, row)
            physical.update({name: row[name] for name in native_columns})
            values.append(physical)
        (r.spark.createDataFrame(values, schema).write.format('delta').mode('overwrite')
         .option('overwriteSchema', 'true').option('txnAppId', 'retained-import').option('txnVersion', seed_version).save(r.paths[RUN]))

    def read(table, **kwargs):
        if table not in registry:
            raise RuntimeError('[PATH_NOT_FOUND]')
        return r.spark.read.format('delta').load(r.paths[RUN]) if table == RUN else r.spark.createDataFrame([], registry[table])

    monkeypatch.setattr(setup, 'read_lakehouse_table', read)
    monkeypatch.setattr(setup, 'write_lakehouse_table', lambda *a, **kw: pytest.fail('existing tables must not be recreated'))
    from fabricops_kit.io import shared as io
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table', lambda *a, **kw: (None, RUN, 'engineering', r.paths[RUN]))

    def migrate():
        return call_with_spark(r.spark, setup.setup_metadata_tables, config=framework_config(), workspace_id='dev', verbose=False)

    from types import SimpleNamespace
    return SimpleNamespace(runtime=r, plan=plan, logical=logical, approval=approval, seed=seed, migrate=migrate,
        read=lambda: read(RUN), version=lambda: r.spark._jvm.org.apache.spark.sql.delta.DeltaLog.forTable(
            r.spark._jsparkSession, r.paths[RUN]).startTransaction().readVersion())


@pytest.mark.parametrize('native_columns', [('operations', 'profiling', 'failures'), ('operations',), ()])
def test_automatic_run_upgrade_retains_approval_hashes_and_idempotency(legacy_run, native_columns):
    """Native/mixed/JSON upgrade never changes a retained approvable Test."""
    f = legacy_run
    f.seed(native_columns)
    from delta.tables import DeltaTable
    r = f.runtime
    before = DeltaTable.forPath(r.spark, r.paths[RUN]).detail().first().asDict()
    version = f.version()
    result = f.migrate()
    assert result['status'] == 'ready', result['table_results']
    migrated = bool(native_columns)
    assert f.version() == version + migrated
    raw = f.read().first().asDict(recursive=True)
    assert all(isinstance(raw[name], str) for name in metadata_json_schema(RUN))
    assert shared.pipeline_record_content(decode_metadata_row(RUN, raw)) == shared.pipeline_record_content(f.logical)
    approval = activation.tested_pipeline_run(testing_run_id=f.plan.plan_id,
        pipeline_name='Orders', pipeline_version='1', agreement_id='agreement', agreement_version='1',
        context=r.context, spark_session=r.spark)
    assert approval['approval_id'] == f.approval['approval_id']
    assert approval['testing_evidence_sha256'] == f.approval['testing_evidence_sha256']
    after = DeltaTable.forPath(r.spark, r.paths[RUN]).detail().first().asDict()
    assert before['id'] == after['id'] and before['properties'] == after['properties']
    assert f.migrate()['status'] == 'ready' and f.version() == version + migrated
    # The migration must retain Delta's SetTransaction actions, not just rows.
    count = f.read().count()
    (r.spark.createDataFrame([raw], metadata_table_schema_registry()[RUN]).write.format('delta').mode('append')
     .option('txnAppId', 'retained-import').option('txnVersion', 7).save(r.paths[RUN]))
    assert f.read().count() == count


@pytest.mark.parametrize('defect', ['duplicate', 'bad_json', 'unknown_field'])
def test_ambiguous_or_corrupt_run_aborts_without_mutation(legacy_run, defect):
    """No retained row is discarded or reinterpreted to make migration succeed."""
    f = legacy_run
    f.seed()
    from delta.tables import DeltaTable
    if defect == 'duplicate':
        f.runtime.spark.createDataFrame([f.logical], metadata_table_schema_registry(logical=True)[RUN]).write.format('delta').mode('append').save(f.runtime.paths[RUN])
    else:
        # Use a supported mixed schema but invalid JSON member content.
        f.seed(native_columns=('operations',))
        value = '{broken' if defect == 'bad_json' else '[{"code":"safe","unknown":true}]'
        DeltaTable.forPath(f.runtime.spark, f.runtime.paths[RUN]).update(set={'failures': "'" + value + "'"})
    version, rows, schema = f.version(), f.read().collect(), f.read().schema
    assert RUN in f.migrate()['failed_tables']
    assert f.version() == version and f.read().collect() == rows and f.read().schema == schema


@pytest.mark.parametrize('fault', ['stage', 'lost_ack'])
def test_run_upgrade_interruption_is_recoverable_without_second_conversion(legacy_run, monkeypatch, fault):
    """Repeated setup follows the committed schema, never replaying pipeline data."""
    f = legacy_run
    f.seed()
    version = f.version()
    with monkeypatch.context() as inject:
        if fault == 'stage':
            from pyspark.sql.readwriter import DataFrameWriter
            original = DataFrameWriter.parquet
            def interrupt(writer, path, *args, **kwargs):
                result = original(writer, path, *args, **kwargs)
                if '_json_upgrade_staging/' in path:
                    raise RuntimeError('interrupted after staging')
                return result
            inject.setattr(DataFrameWriter, 'parquet', interrupt)
        else:
            from py4j.java_gateway import JavaMember
            original = JavaMember.__call__
            def lose_ack(member, *args):
                result = original(member, *args)
                if member.name == 'commit':
                    raise RuntimeError('lost commit acknowledgement')
                return result
            inject.setattr(JavaMember, '__call__', lose_ack)
        assert RUN in f.migrate()['failed_tables']
    assert f.version() == version + (fault == 'lost_ack')
    assert f.migrate()['status'] == 'ready'
    assert f.version() == version + 1
    assert f.migrate()['status'] == 'ready' and f.version() == version + 1
