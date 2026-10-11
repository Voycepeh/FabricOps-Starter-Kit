"""Regression coverage for resolved SCD physical processing payloads."""
# ruff: noqa: D103

from importlib import import_module

import pytest

from fabricops_kit.pipeline.shared import validated_processing

write_module = import_module("fabricops_kit.pipeline.pipeline_write")


@pytest.mark.parametrize(
    ("mode", "parameters"),
    [
        ("scd1", {"key_columns": ["product_id"]}),
        ("scd2", {
            "key_columns": ["product_id"],
            "effective_column": "modified_datetime",
            "tracked_columns": ["price"],
        }),
    ],
)
@pytest.mark.parametrize("source", ["current_authoring", "data_contract"])
def test_physical_scd_processing_excludes_governance_envelope(mode, parameters, source):
    executable = {"load_strategy": mode, **parameters}
    resolved = {
        **executable,
        "source": source,
        "processing_mode": "development_validation",
        "authored_processing": executable,
        "governed_processing": executable if source == "data_contract" else None,
        "contract_id": "contract-1",
        "contract_version": 1,
        "owner_notebook_name": "02_pipeline",
    }
    assert write_module._physical_processing_definition(resolved) == executable
    with pytest.raises(ValueError, match="unsupported fields"):
        validated_processing(resolved)


def test_physical_scd_processing_rejects_unsupported_user_parameter():
    resolved = {
        "load_strategy": "scd1",
        "authored_processing": {
            "load_strategy": "scd1",
            "key_columns": ["product_id"],
            "not_a_valid_parameter": True,
        },
        "governed_processing": None,
    }
    with pytest.raises(ValueError, match="unsupported fields: not_a_valid_parameter"):
        write_module._physical_processing_definition(resolved)


def test_physical_scd_processing_rejects_missing_executable_definition():
    with pytest.raises(ValueError, match="missing its validated executable definition"):
        write_module._physical_processing_definition({
            "load_strategy": "scd1",
            "authored_processing": None,
            "governed_processing": None,
        })


@pytest.mark.parametrize(
    "definition",
    [
        {"load_strategy": "scd1", "key_columns": ["product_id"]},
        {
            "load_strategy": "scd2",
            "key_columns": ["product_id"],
            "effective_column": "modified_datetime",
        },
    ],
)
def test_physical_scd_processing_accepts_plain_validated_definition(definition):
    assert write_module._physical_processing_definition(definition) == definition
