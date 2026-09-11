"""Regression checks for public signatures and NumPy-style documentation."""

from __future__ import annotations

import inspect
import fabricops_kit

from fabricops_kit import check_source_stability, check_freshness, profile_and_register_table


def _assert_numpy_parameter_contract(function) -> None:
    """Require every public parameter to remain documented in a NumPy Parameters section."""
    doc = inspect.getdoc(function) or ""
    assert "\nParameters\n----------\n" in doc
    assert "\nReturns\n-------\n" in doc
    for parameter in inspect.signature(function).parameters.values():
        assert f"\n{parameter.name} :" in doc, f"{function.__name__}.{parameter.name} is missing from its NumPy docstring"


def test_live_observation_checks_keep_their_supported_public_signatures() -> None:
    """Protect the explicitly governed observation-check signatures."""
    assert str(inspect.signature(check_freshness)) == (
        "(observation, *, table_id: str | None = None, enabled: bool = True, "
        "raise_on_failure: bool = False) -> dict"
    )
    assert str(inspect.signature(check_source_stability)) == "(observation, *, target_table_id: str) -> dict"
    assert not hasattr(fabricops_kit, "check_changes")


def test_stage2_touched_public_functions_keep_complete_numpy_parameter_docs() -> None:
    """Prevent metadata refactors from collapsing established public API documentation."""
    for function in (check_source_stability, check_freshness, profile_and_register_table):
        _assert_numpy_parameter_contract(function)
