import importlib
import sys
import types

import fabricops_kit
from fabricops_kit.config import setup_notebook
from fabricops_kit.docs_metadata import PUBLIC_SYMBOL_DOCS


def test_all_exports_are_importable():
    for name in fabricops_kit.__all__:
        assert hasattr(fabricops_kit, name), f"Missing export: {name}"


def test_public_symbol_docs_align_with_all_and_package_root():
    documented = {row["symbol_name"] for row in PUBLIC_SYMBOL_DOCS}
    exported = set(fabricops_kit.__all__)
    allowed_not_documented = {"__version__"}

    missing_from_all = documented - exported
    assert not missing_from_all, f"PUBLIC_SYMBOL_DOCS symbols missing from __all__: {sorted(missing_from_all)}"

    missing_from_root = {name for name in documented if not hasattr(fabricops_kit, name)}
    assert not missing_from_root, f"PUBLIC_SYMBOL_DOCS symbols missing from fabricops_kit root: {sorted(missing_from_root)}"

    undocumented_exports = exported - documented - allowed_not_documented
    assert not undocumented_exports, f"__all__ symbols missing from PUBLIC_SYMBOL_DOCS: {sorted(undocumented_exports)}"


def test_package_root_does_not_expose_internal_helpers():
    allowed_dunders = {"__version__", "__all__", "__doc__", "__file__", "__name__", "__package__", "__path__", "__spec__", "__cached__", "__builtins__"}

    for name in fabricops_kit.__all__:
        assert not name.startswith("_"), f"__all__ should not contain internal symbol: {name}"

    leaked_internal_callables = []
    for name, value in vars(fabricops_kit).items():
        if not name.startswith("_") or name in allowed_dunders:
            continue
        if not callable(value):
            continue
        module_name = getattr(value, "__module__", "")
        if module_name.startswith("fabricops_kit"):
            leaked_internal_callables.append((name, module_name))

    assert not leaked_internal_callables, f"Leaked internal callables at package root: {leaked_internal_callables}"

    explicitly_blocked = {
        "_parse_dq_rules_dict_from_text",
        "_prepare_dq_profile_input_rows",
        "_add_audit_columns",
        "_add_datetime_features",
        "_add_hash_columns",
    }
    leaked_blocked = [name for name in explicitly_blocked if hasattr(fabricops_kit, name)]
    assert not leaked_blocked, f"Internal helpers must not be importable from package root: {sorted(leaked_blocked)}"


def _sample_config():
    from fabricops_kit.config import AIPromptConfig, FrameworkConfig, GovernanceConfig, LineageConfig, NotebookRuntimeConfig, PathConfig, QualityConfig, ReviewWorkflowConfig
    from fabricops_kit.fabric_input_output import FabricStore
    return FrameworkConfig(
        path_config=PathConfig({"Sandbox": {"Source": FabricStore("w", "h", "s", "abfss://s"), "Unified": FabricStore("w", "h2", "u", "abfss://u")}}),
        notebook_runtime_config=NotebookRuntimeConfig(("00_", "02_", "03_")),
        ai_prompt_config=AIPromptConfig("dq", "gov", "ho"),
        quality_config=QualityConfig(),
        governance_config=GovernanceConfig(),
        review_workflow_config=ReviewWorkflowConfig(),
        lineage_config=LineageConfig(),
    )


def test_setup_uses_current_run_id_and_user_fallback(monkeypatch):
    context = {
        "currentNotebookName": "03_pc_test_source_to_unified",
        "currentWorkspaceName": "ws",
        "currentWorkspaceId": "wid",
        "currentRunId": "fabric_run_1",
        "userName": "alice",
        "userId": "u1",
        "isForPipeline": True,
        "isForInteractive": False,
        "isReferenceRun": False,
    }
    runtime_mod = types.SimpleNamespace(context=context)
    monkeypatch.setitem(sys.modules, "notebookutils.runtime", runtime_mod)

    out = setup_notebook(config=_sample_config(), env="Sandbox")
    assert out.run_id == "fabric_run_1"
    assert out.user_name == "alice"


def test_setup_user_falls_back_to_user_id(monkeypatch):
    context = {"currentNotebookName": "03_pc_test_source_to_unified", "currentRunId": "", "userId": "u2"}
    runtime_mod = types.SimpleNamespace(context=context)
    monkeypatch.setitem(sys.modules, "notebookutils.runtime", runtime_mod)
    out = setup_notebook(config=_sample_config(), env="Sandbox")
    assert out.user_name == "u2"
    assert out.run_id
