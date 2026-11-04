"""Setup preserves released Run history and accepted progress on real Delta."""
# ruff: noqa: F811
import hashlib
import importlib
import json
from datetime import datetime

import pytest
from pyspark.sql.types import StructType

from fabricops_kit.config.metadata_schemas import encode_metadata_row, metadata_table_schema_registry
from fabricops_kit.pipeline import shared
from tests.helpers import call_with_spark, framework_config
from tests.integration.test_pipeline_run_delta import runs_delta

pytestmark = pytest.mark.spark
PROVENANCE = {'pipeline_version', 'promotion_id',
              'governed_notebook_id', 'execution_identity', 'run_schema_version'}


@pytest.mark.parametrize('native', [True, False], ids=['native-collections', 'json-collections'])
def test_setup_preserves_retained_runs_and_processing_state(runs_delta, monkeypatch, native):
    """Automatic setup keeps exact historical facts, audit, identity and checkpoints."""
    from delta.tables import DeltaTable
    from fabricops_kit.io import shared as io
    r = runs_delta
    setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')
    registry = metadata_table_schema_registry()
    run_table, state_table = 'METADATA_PIPELINE_RUN', 'METADATA_PROCESSING_STATE'
    plan = r.make(mode='ungoverned')
    r.complete(plan)
    retained = shared.pipeline_run_row(plan, status='succeeded', completed_at=datetime(2025, 1, 2), durable=True)
    retained = shared.validate_pipeline_run(retained)
    retained = {key: value for key, value in retained.items() if key not in PROVENANCE}
    retained['execution_mode'] = 'testing'  # Historical values are facts, not current modes.
    digest = hashlib.sha256(shared.canonical_pipeline_json(shared.pipeline_record_content(retained)).encode()).hexdigest()
    schema = metadata_table_schema_registry(logical=native)[run_table]
    schema = StructType([field for field in schema if field.name not in PROVENANCE])
    stored = retained if native else encode_metadata_row(run_table, retained)
    if not native:
        stored['operations'] = json.dumps(retained['operations'], indent=2, default=str)
    r.spark.createDataFrame([stored], schema).write.format('delta').mode('overwrite').option('overwriteSchema', 'true').save(r.paths[run_table])
    delta = DeltaTable.forPath(r.spark, r.paths[run_table])
    r.spark.sql(f"ALTER TABLE delta.`{r.paths[run_table]}` SET TBLPROPERTIES ('owner_note'='preserved')")
    before_detail = delta.detail().first().asDict()
    r.paths[state_table] = str(r.paths[run_table]) + '-state'
    progress = [{**r.audit, 'record_id': kind, 'record_type': kind, 'status': 'accepted',
                 'workspace_id': 'DEV', 'publication_id': 'verified-publication',
                 'source_table_id': 'table0', 'target_table_id': 'table1',
                 'max_change_value': '2025-01-02T00:00:00', 'watermark_type': 'timestamp'}
                for kind in ('incremental_checkpoint', 'drift_baseline', 'publication_receipt')]
    r.spark.createDataFrame(progress, registry[state_table]).write.format('delta').save(r.paths[state_table])
    state_delta = DeltaTable.forPath(r.spark, r.paths[state_table])
    state_before = r.spark.read.format('delta').load(r.paths[state_table]).collect()
    state_version = state_delta.history(1).first()['version']
    def read(table, **kwargs):
        if table in {run_table, state_table}:
            return r.spark.read.format('delta').load(r.paths[table])
        if table not in registry:
            raise RuntimeError('[PATH_NOT_FOUND]')
        return r.spark.createDataFrame([], registry[table])
    def write(frame, table, **kwargs):
        assert table == run_table and kwargs['mode'] == 'append'
        frame.write.format('delta').mode('append').options(**kwargs['options']).save(r.paths[table])
    monkeypatch.setattr(setup, 'read_lakehouse_table', read)
    monkeypatch.setattr(setup, 'write_lakehouse_table', write)
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table', lambda store, table, schema, **kw: (store, table, schema, r.paths[table]))
    def run_setup():
        return call_with_spark(r.spark, setup.setup_metadata_tables, config=framework_config(), workspace_id='dev', verbose=False)
    assert run_setup()['status'] == 'ready'
    current = r.spark.read.format('delta').load(r.paths[run_table]).first().asDict(recursive=True)
    assert all(current[key] is None for key in PROVENANCE)
    validated = shared.validate_pipeline_run(current)
    assert hashlib.sha256(shared.canonical_pipeline_json(shared.pipeline_record_content(validated)).encode()).hexdigest() == digest
    assert all(current[field.name] == retained[field.name] for field in schema if field.name.startswith('_'))
    if not native:
        assert current['operations'] == stored['operations']
    after_detail = delta.detail().first().asDict()
    assert after_detail['id'] == before_detail['id']
    assert after_detail['properties'] == before_detail['properties']
    version = delta.history(1).first()['version']
    assert run_setup()['status'] == 'ready'
    assert delta.history(1).first()['version'] == version
    assert state_delta.history(1).first()['version'] == state_version
    assert r.spark.read.format('delta').load(r.paths[state_table]).collect() == state_before
    # Normal new execution can append without reinterpreting the retained run.
    fresh = r.make(mode='ungoverned')
    shared.persist_pipeline_run(fresh, spark_session=r.spark)
    rows = r.rows()
    assert len(rows) == 2
    assert next(row for row in rows if row['run_id'] == fresh.plan_id)['run_schema_version'] == 3
