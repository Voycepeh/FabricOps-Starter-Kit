"""Actual Registry candidates cannot open a Governed publication path."""
# ruff: noqa: F811
from copy import deepcopy
from fabricops_kit.activated_pipeline import shared as service
from tests.integration.test_activation_state_delta import authority_delta
from tests.unit.test_activated_pipeline import contract_candidate, PIPELINE_ID
import pytest

pytestmark = pytest.mark.spark


def test_candidate_cutover_never_creates_authorizing_run_or_publication(authority_delta):
    """Retained candidates protect tables while trusted deployment assurance is pending."""
    r = authority_delta
    rows = service.read_registry(context=r.context, spark_session=r.spark)
    wanted = deepcopy(rows) + [{**contract_candidate(), **r.audit}]
    service.commit_registry(wanted, expected_token=service.registry_control(rows)["token"],
        context=r.context, spark_session=r.spark, governance_change=True)
    with pytest.raises(RuntimeError, match="trusted deployment verification"):
        service.build_governed_pipeline_plan(pipeline_id=PIPELINE_ID, context=r.context, spark_session=r.spark)
    assert set(r.paths) == {service.REGISTRY_TABLE}
    assert len(service.read_registry(context=r.context, spark_session=r.spark)) == 2
