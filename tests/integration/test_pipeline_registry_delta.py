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


def test_target_claims_exclude_other_writers_and_can_release(authority_delta):
    """Verify target claims exclude other writers and can release."""
    r = authority_delta
    target = operation()["destination"]
    service.publication_claim("first", target, context=r.context, spark_session=r.spark)
    service.publication_claim("first", target, context=r.context, spark_session=r.spark)
    with pytest.raises(RuntimeError, match="publication lease"):
        service.publication_claim("second", target, context=r.context, spark_session=r.spark)
    service.publication_claim("first", target, context=r.context, spark_session=r.spark, release=True)
    service.publication_claim("second", target, context=r.context, spark_session=r.spark)
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


def test_old_and_new_version_writers_cannot_claim_one_target_concurrently(authority_delta, monkeypatch):
    """Actual concurrent claims admit one version's writer and reject the conflicting publisher."""
    from threading import Barrier
    r = authority_delta
    target = operation()['destination']
    service.publication_claim('seed', target, context=r.context, spark_session=r.spark)
    service.publication_claim('seed', target, context=r.context, spark_session=r.spark, release=True)
    barrier, original = Barrier(2), service.replace_metadata_transaction
    def synchronized(*args, **kwargs):
        barrier.wait(timeout=60)
        return original(*args, **kwargs)
    monkeypatch.setattr(service, 'replace_metadata_transaction', synchronized)
    def claim(owner):
        try:
            service.publication_claim(owner, target, context=r.context, spark_session=r.spark)
            return True
        except Exception:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(claim, ('old-version-run', 'new-version-run'))) == 1
    assert service.read_registry(context=r.context, spark_session=r.spark) == []
