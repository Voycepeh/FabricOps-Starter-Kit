from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from fabricops_kit.config import (
    AIPromptConfig,
    DatasetContractValidationError,
    FrameworkConfig,
    GovernanceConfig,
    LineageConfig,
    NotebookRuntimeConfig,
    PathConfig,
    QualityConfig,
    ReviewWorkflowConfig,
    assert_valid_dataset_contract,
    load_dataset_contract,
    setup_notebook,
)
from fabricops_kit.data_agreement import _latest_agreement_versions, _render_custom_fields
from fabricops_kit.data_quality import validate_dq_rules
from fabricops_kit.fabric_input_output import FabricStore, read_lakehouse_excel, read_lakehouse_table
from fabricops_kit.metadata import register_current_notebook

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("value", [None, "", "   ", 123, [], {}])
def test_fabric_store_rejects_invalid_required_strings(value):
    with pytest.raises(ValueError, match="workspace_id must be a non-empty string"):
        FabricStore(env="dev", workspace_id=value, item_id="item", name="Lakehouse", kind="lakehouse")


def test_fabric_store_rejects_unknown_kind():
    with pytest.raises(ValueError, match="kind must be one of"):
        FabricStore(env="dev", workspace_id="workspace", item_id="item", name="Lakehouse", kind="eventhouse")


@pytest.mark.parametrize("paths", [None, {}, [], "dev"])
def test_path_config_rejects_invalid_environment_mapping(paths):
    with pytest.raises(ValueError, match="paths must be a non-empty mapping"):
        PathConfig(paths=paths)  # type: ignore[arg-type]


def _framework_config_with_store() -> FrameworkConfig:
    store = FabricStore(env="dev", workspace_id="workspace", item_id="item", name="Lakehouse", kind="lakehouse")
    return FrameworkConfig(
        path_config=PathConfig(paths={"dev": {"Source": store, "metadata": store, "source": store}}),
        notebook_runtime_config=NotebookRuntimeConfig(),
        ai_prompt_config=AIPromptConfig("context", "dq", "personal", "candidate", "review", "handover"),
        quality_config=QualityConfig(),
        governance_config=GovernanceConfig(),
        review_workflow_config=ReviewWorkflowConfig(),
        lineage_config=LineageConfig(),
    )


def test_setup_notebook_reports_invalid_environment_name():
    with pytest.raises(ValueError, match="Environment 'prod' was not found"):
        setup_notebook(_framework_config_with_store(), env="prod", required_targets=["Source"], notebook_name="02_ex_orders_customers")


def test_dataset_contract_wraps_non_mapping_yaml_for_safe_validation(tmp_path: Path):
    path = tmp_path / "contract.yaml"
    path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    contract = load_dataset_contract(path)

    assert contract == {"value": ["not", "a", "mapping"]}
    with pytest.raises(DatasetContractValidationError, match="Dataset contract validation failed"):
        assert_valid_dataset_contract(contract)


def test_dataset_contract_reports_missing_required_fields():
    with pytest.raises(DatasetContractValidationError, match="required"):
        assert_valid_dataset_contract({"dataset": {"name": "orders"}})


@pytest.mark.parametrize(
    ("rules", "message"),
    [
        (None, "DQ rules must be a list"),
        (["bad"], "must be a dictionary"),
        ([{"rule_id": "r1"}], "missing fields"),
        (
            [{"rule_id": "r1", "rule_type": "unknown", "columns": ["id"], "severity": "error", "description": "x"}],
            "unsupported rule_type",
        ),
        (
            [{"rule_id": "r1", "rule_type": "not_null", "columns": [], "severity": "error", "description": "x"}],
            "columns must be a non-empty list",
        ),
    ],
)
def test_validate_dq_rules_negative_cases(rules, message):
    with pytest.raises(ValueError, match=message):
        validate_dq_rules(rules)  # type: ignore[arg-type]


def test_custom_field_config_rejects_missing_key(monkeypatch):
    widgets = SimpleNamespace(Text=lambda **kwargs: kwargs)
    monkeypatch.setattr("fabricops_kit.data_agreement._require_ipywidgets", lambda: widgets)

    with pytest.raises(KeyError, match="key"):
        _render_custom_fields([{"type": "text"}])


def test_read_lakehouse_table_reports_invalid_environment_name():
    with pytest.raises(ValueError, match="Environment 'prod' was not found"):
        read_lakehouse_table(_framework_config_with_store(), "prod", "metadata", "METADATA_TEST", spark_session=object())


def test_excel_reader_rejects_missing_file_path():
    with pytest.raises(ValueError, match="relative_path must be a non-empty string"):
        read_lakehouse_excel(_framework_config_with_store(), "dev", "source", "   ", spark_session=object())


def test_register_current_notebook_requires_metadata_route():
    with pytest.raises(ValueError, match="requires config and env"):
        register_current_notebook(spark=object(), agreement_id="DA-1")


def test_latest_agreement_versions_use_stable_tie_breaking():
    rows = [
        {"agreement_id": "DA-1", "agreement_name": "Orders", "contract_version": "1.0.0", "_committed_at": "2026-06-01T00:00:00Z"},
        {"agreement_id": "DA-1", "agreement_name": "Orders", "contract_version": "1.0.0", "_committed_at": "2026-06-02T00:00:00Z"},
        {"agreement_id": "DA-2", "agreement_name": "Customers", "contract_version": "1.0.1", "_committed_at": "2026-06-01T00:00:00Z"},
    ]

    latest = _latest_agreement_versions(list(reversed(rows)))

    assert latest == [rows[2], rows[1]]
