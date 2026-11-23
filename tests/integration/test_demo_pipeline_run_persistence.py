"""00C-to-02A lifecycle with simulated Fabric services and real CSV/Delta storage."""
# ruff: noqa: F811, D103
import importlib
import os
from datetime import UTC, datetime
from pathlib import Path
import time

import pytest

from fabricops_kit import finalize_pipeline, orchestrate_demo_reset, orchestrate_read, setup_pipeline
from fabricops_kit.pipeline import shared
from tests.integration.test_pipeline_run_delta import runs_delta
from tests.unit.test_orchestrate_demo_reset import _ready
from tests.unit.test_unified_file_read import files
from tests.unit.test_pipeline_session import runtime

MERGE_RUN = shared._merge_pipeline_run_row
READ_CSV = importlib.import_module('fabricops_kit.io.read_lakehouse_csv').read_lakehouse_csv
ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.spark


@pytest.mark.parametrize('retained_columns', [False, True])
def test_reset_then_02a_reads_and_finalizes_in_fresh_sessions(files, runs_delta, monkeypatch, retained_columns):
    """Keep Run history across reset, then update one Run per fresh-session file read."""
    r = runs_delta
    if retained_columns:
        path = r.paths['METADATA_PIPELINE_RUN']
        r.spark.sql(f"ALTER TABLE delta.`{path}` ADD COLUMNS (approval_id STRING, activation_revision STRING)")
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', MERGE_RUN)
    monkeypatch.setattr(shared, 'get_spark_session', lambda supplied=None, **kw: supplied or r.spark)
    r.audit['_committed_at'] = datetime.now(UTC)
    retained = r.make(mode='ungoverned')
    shared.persist_pipeline_run(retained, spark_session=r.spark)
    history = shared._read_pipeline_run_rows(retained, spark_session=r.spark)[0]
    # The reset's remote Fabric services are simulated. Its real reset controller
    # is already covered against physical Delta by test_demo_reset_spark.
    env = _ready(monkeypatch)
    env.rows['METADATA_PIPELINE_RUN'].append({'run_id': 'retained-history'})
    orchestrate_demo_reset(reset=True)
    assert env.rows['METADATA_PIPELINE_RUN'] == [{'run_id': 'retained-history'}]
    io = importlib.import_module('fabricops_kit.io')
    monkeypatch.setattr(io, 'read_lakehouse_csv', READ_CSV)
    reader = importlib.import_module('fabricops_kit.io.read_lakehouse_csv')
    monkeypatch.setattr(reader, 'resolve_configured_file_path', lambda store, path, **kw:
        (files.configured, path, str(ROOT / 'templates/DemoData' / Path(path).name)))
    monkeypatch.setattr(files.runtime.read, 'schedule_file_profiling', lambda *a, **kw:
        {'status': 'skipped', 'row_count': None, 'results_persisted': False})
    previous_zone = os.environ.get('TZ')
    os.environ['TZ'] = 'Asia/Singapore'
    time.tzset()
    try:
        completed = []
        for _ in range(2):
            # newSession discards SQL/session state while retaining persisted files.
            r.spark = r.spark.newSession()
            r.spark.conf.set('spark.sql.session.timeZone', 'Asia/Singapore')
            session = setup_pipeline(pipeline_mode='Ungoverned', profiling_enabled=False)
            source = orchestrate_read(store='Bronze', relative_path='demo/orders.csv', file_format='csv')
            assert source['dataframe'].count() == 120
            persisted = [shared.validate_pipeline_run(row) for row in
                         shared._read_pipeline_run_rows(session.plan, spark_session=r.spark)]
            assert len(persisted) == 1 and persisted[0]['status'] == 'incomplete'
            assert persisted[0]['operations'][0]['status'] == 'succeeded'
            assert persisted[0]['operations'][0]['destination']['relative_path'] == 'demo/orders.csv'
            result = finalize_pipeline(session)
            assert result['status'] == 'ungoverned_completed'
            completed.append(session.plan.plan_id)
            rows = r.rows()
            assert len(rows) == len(completed) + 1
            assert {row['run_id'] for row in rows} == {*completed, retained.plan_id}
            assert all(row['completed_at'] is not None for row in rows if row['run_id'] in completed)
            assert shared._read_pipeline_run_rows(retained, spark_session=r.spark) == [history]
        assert env.rows['METADATA_PIPELINE_RUN'] == [{'run_id': 'retained-history'}]
    finally:
        if previous_zone is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = previous_zone
        time.tzset()
