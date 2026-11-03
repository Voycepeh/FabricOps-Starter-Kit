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
