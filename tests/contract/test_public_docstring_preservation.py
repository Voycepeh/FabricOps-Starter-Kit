"""Regression checks for public signatures and NumPy-style documentation."""

from __future__ import annotations

import inspect
import fabricops_kit

from fabricops_kit import profile_table
from fabricops_kit.pipeline.check_source_drift import check_source_drift
from fabricops_kit.pipeline.check_freshness import check_freshness


def _assert_numpy_parameter_contract(function) -> None:
    """Require every public parameter to remain documented in a NumPy Parameters section."""
    doc = inspect.getdoc(function) or ""
    assert "\nParameters\n----------\n" in doc
    assert "\nReturns\n-------\n" in doc
    for parameter in inspect.signature(function).parameters.values():
        assert f"\n{parameter.name} :" in doc, (
            f"{function.__name__}.{parameter.name} is missing from its NumPy docstring"
        )


def test_orchestrators_are_the_public_pipeline_execution_entrypoints() -> None:
    """Orchestrators and the read capability remain public; other stages stay internal."""
    assert callable(fabricops_kit.orchestrate_read)
    assert callable(fabricops_kit.orchestrate_write)
    assert callable(fabricops_kit.pipeline_read)
    for name in ("pipeline_write", "check_freshness", "check_schema",
                 "check_dq", "check_source_drift", "check_sensitive_data"):
        assert not hasattr(fabricops_kit, name)


def test_public_orchestrators_keep_complete_numpy_parameter_docs() -> None:
    """Every public workflow parameter remains documented, including token mapping reuse."""
    for function in (fabricops_kit.orchestrate_read, fabricops_kit.orchestrate_write, profile_table):
        _assert_numpy_parameter_contract(function)
