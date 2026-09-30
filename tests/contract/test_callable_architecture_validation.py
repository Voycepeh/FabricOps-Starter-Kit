"""Tests for warning-first callable architecture validation."""

from __future__ import annotations

import pytest

from scripts import validate_callable_architecture as validator


def test_structural_source_findings_are_blocking() -> None:
    """Verify public/internal boundary violations remain blocking."""
    assert validator.classify_source_finding(
        "Public function calls public function: fabricops_kit.a.public_a -> fabricops_kit.b.public_b"
    ) == "failure"
    assert validator.classify_source_finding(
        "Internal function calls public function: fabricops_kit.a.internal_a -> fabricops_kit.b.public_b"
    ) == "failure"


@pytest.mark.parametrize(
    "message",
    [
        "Private helper called outside owner file: fabricops_kit.a.public_a -> fabricops_kit.b._helper",
        "Private helper imported outside owner file: fabricops_kit.a.public_a imports fabricops_kit.b._helper as _helper",
        "Shared helper is underscore-prefixed but used by multiple public function files: fabricops_kit.a._helper (a.py, b.py)",
    ],
)
def test_cleanup_findings_are_warnings(message: str) -> None:
    """Verify refactor cleanup findings are warnings by default."""
    assert validator.classify_source_finding(message) == "warning"


def test_default_mode_exits_zero_for_warnings_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify default validation accepts warning-only cleanup debt."""
    monkeypatch.setattr(
        validator,
        "validate",
        lambda: validator.ValidationResult(failures=[], warnings=["Private helper called outside owner file: x -> y"]),
    )
    assert validator.main([]) == 0


def test_strict_mode_exits_nonzero_for_warnings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify strict validation promotes warnings to failures."""
    monkeypatch.setattr(
        validator,
        "validate",
        lambda: validator.ValidationResult(failures=[], warnings=["Private helper called outside owner file: x -> y"]),
    )
    assert validator.main(["--strict"]) == 1
