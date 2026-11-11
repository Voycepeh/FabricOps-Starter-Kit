"""Engineering-owned processing validation has no Data Contract dependency."""
import pytest
from fabricops_kit.pipeline.shared import validated_processing, validated_pipeline_processing


@pytest.mark.parametrize("mode,parameters", [("overwrite", {}), ("append_all", {}), ("append_new_only", {}),
    ("scd1", {"key_columns": ["id"]}), ("scd2", {"key_columns": ["id"], "effective_column": "modified_dt"})])
def test_pipeline_owns_every_supported_write_strategy(mode, parameters):
    """Each supported strategy is valid without contract Processing configuration."""
    exact = validated_pipeline_processing(role="target", read_mode=None, read_parameters=None,
        write_mode=mode, write_parameters=parameters, repartition_by=None)
    assert exact["write_parameters"] == parameters
    assert validated_processing({"load_strategy": mode, **parameters})["load_strategy"] == mode


@pytest.mark.parametrize("processing", [None, {}, {"load_strategy": "merge"}, {"load_strategy": "scd2", "key_columns": ["id"]}])
def test_invalid_engineering_processing_rejects(processing):
    """Moving processing ownership does not weaken strategy validation."""
    with pytest.raises(ValueError):
        validated_processing(processing)


def test_approval_parameters_are_snapshotted():
    """Later caller mutations cannot edit captured processing configuration."""
    proposed = {"key_columns": ["id"], "effective_column": "modified_dt"}
    approved = validated_pipeline_processing(role="target", read_mode=None, read_parameters=None,
        write_mode="scd2", write_parameters=proposed, repartition_by=2)
    proposed["key_columns"].append("other")
    assert approved["write_parameters"]["key_columns"] == ["id"]
