"""SCD executable definitions contain Engineering processing parameters only."""
import pytest
from fabricops_kit.pipeline.shared import validated_processing


@pytest.mark.parametrize("mode,parameters", [("scd1", {"key_columns": ["id"]}),
    ("scd2", {"key_columns": ["id"], "effective_column": "modified_dt", "tracked_columns": ["amount"]})])
def test_scd_definitions_are_plain_engineering_configuration(mode, parameters):
    """SCD execution needs no contract resolution envelope or compatibility wrapper."""
    definition = {"load_strategy": mode, **parameters}
    assert validated_processing(definition) == definition


@pytest.mark.parametrize("removed", ["contract_id", "contract_version", "source", "authored_processing", "governed_processing"])
def test_contract_processing_envelope_is_rejected(removed):
    """Removed contract processing fields cannot re-enter executable definitions."""
    with pytest.raises(ValueError, match="unsupported fields"):
        validated_processing({"load_strategy": "scd1", "key_columns": ["id"], removed: "obsolete"})
