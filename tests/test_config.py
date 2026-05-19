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
