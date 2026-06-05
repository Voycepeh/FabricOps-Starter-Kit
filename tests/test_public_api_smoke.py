import pytest

pytestmark = pytest.mark.contract
import fabricops_kit as kit


def test_package_import_and_core_entrypoints_available():
    assert not hasattr(kit, "load_config")
    assert callable(kit.setup_data_agreement_tables)
    assert not hasattr(kit, "validate_data_agreement_prerequisites")
    assert not hasattr(kit, "DATA_STEWARD_REQUIRED_FIELDS")
    assert not hasattr(kit, "DATA_STEWARD_SYSTEM_FIELDS")
    assert callable(kit.setup_notebook)
    assert callable(kit.profile_dataframe)
    assert callable(kit.read_lakehouse_excel)
    assert callable(kit.validate_dq_rules)
    assert callable(kit.build_handover)


def test_obsolete_data_agreement_setup_module_removed():
    from pathlib import Path

    assert not Path("src/fabricops_kit/data_agreement_setup.py").exists()
