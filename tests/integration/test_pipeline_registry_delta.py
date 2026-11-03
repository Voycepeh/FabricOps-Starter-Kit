"""Registry control initialization is persistent and SQL-compatible."""
# ruff: noqa: F811
from fabricops_kit.activated_pipeline import shared as service
from tests.integration.test_activation_state_delta import authority_delta
import pytest

pytestmark = pytest.mark.spark


def test_control_seed_is_retained_and_all_columns_are_scalar(authority_delta):
    """Reads preserve the token and never manufacture registrations."""
    r = authority_delta
    first = service.read_registry(context=r.context, spark_session=r.spark)
    second = service.read_registry(context=r.context, spark_session=r.spark)
    assert first == second and len(first) == 1
    assert first[0]["record_type"] == "control"
    assert all(not hasattr(field.dataType, "fields") and not hasattr(field.dataType, "elementType")
        for field in r.spark.read.format("delta").load(r.path).schema)


def test_concurrent_managed_append_admission_has_one_target_lease(authority_delta, monkeypatch):
    """Two append attempts cannot both compare hashes or publish the same target snapshot."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from types import SimpleNamespace
    from tests.unit.test_activated_pipeline import operation, PIPELINE_ID
    import json
    r, barrier = authority_delta, Barrier(2)
    original = service.replace_registry_transaction
    def synchronize(*args, **kwargs):
        barrier.wait(timeout=45)
        return original(*args, **kwargs)
    monkeypatch.setattr(service, 'replace_registry_transaction', synchronize)
    def admit(run_id):
        plan = SimpleNamespace(runtime_context=r.context, workspace_id='DEV', pipeline_id=PIPELINE_ID,
                               plan_id=run_id, evidence={})
        try:
            service.guard_ungoverned_write(plan, 'orders', operation()['destination'], spark_session=r.spark)
            return True
        except Exception:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(admit, ('first', 'second'))) == 1
    leases = json.loads(service.registry_control(service.read_registry(context=r.context, spark_session=r.spark))['leases_json'])
    assert len(leases) == 1
    assert leases[0]['run_id'] in {'first', 'second'}
