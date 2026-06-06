from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import fabricops_kit
from fabricops_kit import governance_review
from fabricops_kit.metadata import get_notebook_registry_schema

pytestmark = pytest.mark.contract


def test_supported_public_functions_import_and_keep_core_signatures():
    required = {
        "setup_notebook",
        "read_lakehouse_table",
        "write_lakehouse_table",
        "read_lakehouse_csv",
        "read_lakehouse_parquet",
        "read_lakehouse_excel",
        "write_warehouse_table",
        "profile_dataframe",
        "validate_schema",
        "monitor_data_changes",
        "enforce_dq",
        "build_handover",
        "widget_select_agreement",
        "setup_data_agreement_tables",
        "setup_governance_metadata_tables",
        "register_current_notebook",
    }

    assert required.issubset(set(fabricops_kit.__all__))
    for name in required:
        assert callable(getattr(fabricops_kit, name))
    assert "config" in inspect.signature(fabricops_kit.setup_notebook).parameters
    assert "table_name" in inspect.signature(fabricops_kit.enforce_dq).parameters
    assert "env" in inspect.signature(fabricops_kit.register_current_notebook).parameters


def test_essential_metadata_schemas_and_notebook_templates_exist():
    templates = Path(__file__).parents[2] / "templates" / "notebooks"
    expected_templates = {
        "00_env_config.ipynb",
        "01_da_agreement_template.ipynb",
        "02_ex_agreement_topic.ipynb",
        "03_pc_agreement_pipeline_template.ipynb",
        "04_gov_agreement_dataset_table.ipynb",
        "04_gov_dataset_table.ipynb",
    }
    governance_schemas = governance_review.get_governance_metadata_schemas()

    assert expected_templates.issubset({path.name for path in templates.glob("*.ipynb")})
    assert {"agreement_id", "notebook_name", "registration_id", "registration_status"}.issubset(get_notebook_registry_schema())
    assert {"METADATA_DATA_CATALOGUE", "METADATA_COLUMN_CONTEXT", "METADATA_DQ_RULES", "METADATA_COLUMN_CLASSIFICATION"}.issubset(governance_schemas)
    assert governance_schemas["METADATA_DQ_RULES"].fieldNames()
