"""Persisted promotions do not override the pending Fabric validation gate."""
# ruff: noqa: F811
from fabricops_kit.activated_pipeline import shared as service
from tests.integration.test_activation_state_delta import authority_delta
from tests.unit.test_activated_pipeline import PIPELINE_ID
import pytest

pytestmark = pytest.mark.spark


def test_active_row_alone_never_authorizes_governed_run(authority_delta):
    """Verify active row alone never authorizes governed run."""
    r = authority_delta
    service.commit_pipeline_promotion(r.candidate(), expected_active_version=None, context=r.context, spark_session=r.spark)
    with pytest.raises(RuntimeError, match="signed-in Fabric"):
        service.build_governed_pipeline_plan(pipeline_id=PIPELINE_ID, context=r.context, spark_session=r.spark)
    assert set(r.paths) == {service.REGISTRY_TABLE}
