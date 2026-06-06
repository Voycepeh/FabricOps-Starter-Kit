from __future__ import annotations

from pathlib import Path

import pytest

from fabricops_kit.config import (
    DataAgreementConfig,
    DatasetContractValidationError,
    PathConfig,
    assert_valid_dataset_contract,
    load_dataset_contract,
    setup_notebook,
    validate_dataset_contract,
)
from tests.helpers import framework_config

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_dataset_contract_valid_and_invalid_paths_are_actionable():
    valid = load_dataset_contract(FIXTURES / "valid_dataset_contract.yaml")
    invalid = load_dataset_contract(FIXTURES / "invalid_dataset_contract_missing_required.yaml")

    assert validate_dataset_contract(valid) == []
    errors = validate_dataset_contract(invalid)
    assert errors
    assert any("required property" in error for error in errors)
    with pytest.raises(DatasetContractValidationError):
        assert_valid_dataset_contract(invalid)


def test_setup_notebook_resolves_environment_paths_and_reports_invalid_targets(fake_notebookutils):
    config = framework_config()

    context = setup_notebook(config=config, env="dev", required_targets=["source", "metadata"], notebook_name="02_ex_orders")

    assert context.environment == "dev"
    assert set(context.paths) == {"source", "metadata"}
    assert context.readiness_status in {"ready", "not_ready"}
    with pytest.raises(ValueError, match="Target 'missing' was not found"):
        setup_notebook(config=config, env="dev", required_targets=["missing"])


def test_config_objects_copy_nested_agreement_defaults_and_validate_paths():
    source = {"visible_columns": ["steward_name"], "custom_fields": [{"key": "group", "options": ["A"]}]}
    config = DataAgreementConfig(data_steward_widget=source)
    source["custom_fields"][0]["options"].append("B")

    assert config.data_steward_widget["custom_fields"][0]["options"] == ["A"]
    assert "data_agreement_evidence" in config.metadata_tables
    assert {"recipient", "approved_usage_internal", "approved_usage_external", "approved_usage_research"}.issubset(
        set(config.data_agreement_widget["visible_columns"])
    )
    with pytest.raises(ValueError, match="paths must be a non-empty mapping"):
        PathConfig(paths={})
