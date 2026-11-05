"""Registry contains only immutable pipeline versions; claims live in Metadata Files."""
# ruff: noqa: F811
from concurrent.futures import ThreadPoolExecutor
from fabricops_kit.activated_pipeline import shared as service
from tests.integration.test_activation_state_delta import authority_delta
from tests.unit.test_activated_pipeline import operation
import pytest

pytestmark = pytest.mark.spark


def test_fresh_registry_is_empty_and_does_not_manufacture_control(authority_delta):
    """Verify fresh registry is empty and does not manufacture control."""
    r = authority_delta
    assert service.read_registry(context=r.context, spark_session=r.spark) == []
    assert service.read_registry(context=r.context, spark_session=r.spark) == []




def test_complete_notebook_archive_is_write_once_and_exact(authority_delta, tmp_path):
    """Actual Hadoop file writes retain all ipynb bytes and refuse overwrite."""
    from tests.unit.test_activated_pipeline import notebook
    r = authority_delta
    uri = str(tmp_path / "Files" / "pipeline_snapshots" / "notebook.ipynb")
    original = notebook()
    assert service.snapshot_file(uri, spark_session=r.spark, content=original) == original
    assert service.snapshot_file(uri, spark_session=r.spark) == original
    with pytest.raises(Exception):
        service.snapshot_file(uri, spark_session=r.spark, content=notebook("changed = True"))
    assert service.snapshot_file(uri, spark_session=r.spark) == original


@pytest.mark.parametrize('parallelism', [5, 10, 20])
def test_independent_workspace_promotions_survive_shared_snapshot_conflicts(authority_delta, monkeypatch, parallelism):
    """All workspace-specific approvals survive collisions in one shared Registry."""
    from threading import Barrier, local
    r = authority_delta
    ready, state = Barrier(parallelism), local()
    original = service.replace_metadata_transaction
    def collide_first_attempt(*args, **kwargs):
        if not getattr(state, 'started', False):
            state.started = True
            ready.wait(timeout=120)
        return original(*args, **kwargs)
    monkeypatch.setattr(service, 'replace_metadata_transaction', collide_first_attempt)
    def promote(index):
        candidate = r.candidate(workspace=f'workspace-{index}')
        candidate['_committed_by'] = f'engineer-{index}'
        return service.commit_pipeline_promotion(candidate, expected_active_version=None,
            context=r.context, spark_session=r.spark)
    with ThreadPoolExecutor(parallelism) as pool:
        results = list(pool.map(promote, range(parallelism)))
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    assert len(rows) == len(results) == parallelism
    assert len({row['execution_workspace_id'] for row in rows}) == parallelism
    assert len({row['_committed_by'] for row in rows}) == parallelism
