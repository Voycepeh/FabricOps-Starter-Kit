from __future__ import annotations

import importlib
import pkgutil

import fabricops_kit
import pytest

pytestmark = pytest.mark.contract


def test_all_fabricops_modules_import_outside_fabric(fake_notebookutils):
    """Importing modules must not require a live Fabric workspace or notebook runtime."""

    failures = []
    for module_info in pkgutil.walk_packages(fabricops_kit.__path__, prefix=f"{fabricops_kit.__name__}."):
        try:
            importlib.import_module(module_info.name)
        except Exception as exc:  # pragma: no cover - failure path reports all modules
            failures.append(f"{module_info.name}: {type(exc).__name__}: {exc}")

    assert failures == []
