from __future__ import annotations

import builtins
import importlib
import sys

import pytest

OPTIONAL_IMPORT_ROOTS = {"openai", "pydantic", "ipywidgets", "networkx", "matplotlib"}

pytestmark = pytest.mark.contract


@pytest.fixture
def block_optional_imports(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        root = name.split(".", 1)[0]
        if root in OPTIONAL_IMPORT_ROOTS:
            raise ModuleNotFoundError(f"No module named '{root}'")
        return original_import(name, globals, locals, fromlist, level)

    for module_name in list(sys.modules):
        if module_name.split(".", 1)[0] in OPTIONAL_IMPORT_ROOTS or module_name == "fabricops_kit" or module_name.startswith("fabricops_kit."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)
    monkeypatch.setattr(builtins, "__import__", guarded_import)


def test_base_package_imports_without_optional_extras(block_optional_imports, fake_notebookutils):
    kit = importlib.import_module("fabricops_kit")

    assert kit.__version__
    assert callable(kit.setup_notebook)
    assert callable(kit.build_lineage_records)


def test_widget_feature_reports_actionable_optional_extra(block_optional_imports):
    data_agreement = importlib.import_module("fabricops_kit.data_agreement")

    with pytest.raises(ModuleNotFoundError, match="fabricops-kit\[dq-review\]"):
        data_agreement._render_custom_fields([{"key": "review_note", "type": "text"}])
