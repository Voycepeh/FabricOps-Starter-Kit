from pathlib import Path

import pytest

from fabricops_kit.config import (
    DatasetContractValidationError,
    assert_valid_dataset_contract,
    load_and_validate_dataset_contract,
    load_dataset_contract,
    validate_dataset_contract,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_FIXTURE = FIXTURES_DIR / "valid_dataset_contract.yaml"
INVALID_FIXTURE = FIXTURES_DIR / "invalid_dataset_contract_missing_required.yaml"


def test_load_and_validate_dataset_contract_smoke():
    contract = load_dataset_contract(VALID_FIXTURE)
    assert contract["dataset"]["name"]
    assert validate_dataset_contract(contract) == []


def test_invalid_contract_reports_errors_and_assertion_raises():
    bad_contract = load_dataset_contract(INVALID_FIXTURE)
    errors = validate_dataset_contract(bad_contract)
    assert errors

    with pytest.raises(DatasetContractValidationError):
        assert_valid_dataset_contract(bad_contract)


def test_load_and_validate_dataset_contract_returns_contract_and_errors():
    contract, errors = load_and_validate_dataset_contract(INVALID_FIXTURE)
    assert isinstance(contract, dict)
    assert errors


def test_setup_notebook_validates_config_sections_and_required_targets():
    from fabricops_kit.config import (
        AIPromptConfig,
        FrameworkConfig,
        GovernanceConfig,
        LineageConfig,
        NotebookRuntimeConfig,
        PathConfig,
        QualityConfig,
        ReviewWorkflowConfig,
        setup_notebook,
    )

    class Store:
        workspace_id = "workspace"
        item_id = "item"
        name = "source"
        kind = "lakehouse"

    with pytest.raises(ValueError, match="missing required keys"):
        setup_notebook(config={}, env="dev", required_targets=["source"])

    config = FrameworkConfig(
        path_config=PathConfig(paths={"dev": {"source": Store()}}),
        notebook_runtime_config=NotebookRuntimeConfig(),
        ai_prompt_config=AIPromptConfig("context", "dq", "personal", "candidate", "review", "handover"),
        quality_config=QualityConfig(),
        governance_config=GovernanceConfig(),
        review_workflow_config=ReviewWorkflowConfig(),
        lineage_config=LineageConfig(),
    )
    with pytest.raises(ValueError, match="Target 'metadata' was not found"):
        setup_notebook(config=config, env="dev", required_targets=["source", "metadata"])
