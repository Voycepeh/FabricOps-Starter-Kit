import fabricops_kit as kit


def test_package_import_and_core_entrypoints_available():
    assert callable(kit.load_config)
    assert callable(kit.setup_notebook)
    assert callable(kit.profile_dataframe)
    assert callable(kit.validate_dq_rules)
    assert callable(kit.build_handover)
