from __future__ import annotations

from pathlib import Path

import pytest

from fabricops_kit.config import (
    DataAgreementConfig,
    DatasetContractValidationError,
    PathConfig,
    _assert_valid_dataset_contract,
    _load_dataset_contract,
    setup_metadata_tables,
    setup_notebook,
    _validate_dataset_contract,
)
from tests.helpers import framework_config

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_dataset_contract_valid_and_invalid_paths_are_actionable():
    valid = _load_dataset_contract(FIXTURES / "valid_dataset_contract.yaml")
    invalid = _load_dataset_contract(FIXTURES / "invalid_dataset_contract_missing_required.yaml")

    assert _validate_dataset_contract(valid) == []
    errors = _validate_dataset_contract(invalid)
    assert errors
    assert any("required property" in error for error in errors)
    with pytest.raises(DatasetContractValidationError):
        _assert_valid_dataset_contract(invalid)


def test_setup_notebook_resolves_environment_paths_and_reports_invalid_targets(fake_notebookutils):
    config = framework_config()

    required_targets = ["source", "unified", "product", "metadata"]
    context = setup_notebook(
        config=config, env="dev", required_targets=required_targets, notebook_name="99_explore_orders"
    )

    assert context.environment == "dev"
    assert set(context.paths) == set(required_targets)
    assert context.paths["source"].name == "lh_source_dev"
    assert context.paths["unified"].name == "lh_unified_dev"
    assert context.paths["product"].name == "wh_product_dev"
    assert context.paths["metadata"].name == "lh_metadata_dev"
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


def test_setup_metadata_tables_delegates_v1_metadata_setup(monkeypatch):
    calls = []

    def data_agreement_setup(**kwargs):
        calls.append(("data_agreement", kwargs))
        return {"status": "ready", "created_tables": []}

    def notebook_registry_setup(**kwargs):
        calls.append(("notebook_registry", kwargs))
        return {"status": "ready", "created_tables": []}

    def governance_setup(**kwargs):
        calls.append(("governance", kwargs))
        return {"status": "ready", "created_tables": []}

    monkeypatch.setattr("fabricops_kit.data_agreement._setup_data_agreement_tables", data_agreement_setup)
    monkeypatch.setattr("fabricops_kit.metadata._setup_notebook_registry_table", notebook_registry_setup)
    monkeypatch.setattr("fabricops_kit.governance_review._setup_governance_metadata_tables", governance_setup)

    config = framework_config()
    spark = object()
    result = setup_metadata_tables(spark=spark, config=config, env="dev", require_active_steward=True)

    assert result["status"] == "ready"
    assert [name for name, _ in calls] == ["data_agreement", "notebook_registry", "governance"]
    assert calls[0][1] == {"spark": spark, "config": config, "env": "dev", "require_active_steward": True}
    assert calls[1][1] == {"spark": spark, "config": config, "env": "dev"}
    assert calls[2][1] == {"spark": spark, "config": config, "env": "dev"}


def test_setup_metadata_tables_treats_clean_agreement_intake_as_bootstrap_ready(monkeypatch):
    monkeypatch.setattr(
        "fabricops_kit.data_agreement._setup_data_agreement_tables",
        lambda **kwargs: {"status": "not_ready", "created_tables": ["METADATA_DATA_STEWARD"], "active_steward_count": 0},
    )
    monkeypatch.setattr(
        "fabricops_kit.metadata._setup_notebook_registry_table",
        lambda **kwargs: {"status": "ready", "created_tables": []},
    )
    monkeypatch.setattr(
        "fabricops_kit.governance_review._setup_governance_metadata_tables",
        lambda **kwargs: {"status": "ready", "created_tables": []},
    )

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["data_agreement"]["status"] == "not_ready"


def test_governance_review_imports_current_prompt_constants():
    import fabricops_kit.governance_review as governance_review

    assert governance_review.BUSINESS_CONTEXT_PROMPT.strip()
    assert governance_review.PDPA_PERSONAL_IDENTIFIER_PROMPT.strip()
