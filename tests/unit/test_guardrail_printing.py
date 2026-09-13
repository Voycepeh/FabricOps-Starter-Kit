"""Tests for standardized public Guardrail status output."""

from __future__ import annotations

import inspect

import pytest

from fabricops_kit import check_dq, check_freshness, check_schema, check_sensitive_data
from fabricops_kit.pipeline.shared import print_guardrail_result

pytestmark = pytest.mark.unit


def test_dataframe_guardrail_public_signatures_are_consistent() -> None:
    """DataFrame checks use a DataFrame-first interface and shared controls."""
    assert str(inspect.signature(check_schema)) == (
        "(dataframe=None, *, table_id: str, enabled: bool = True, "
        "raise_on_failure: bool = False, verbose: bool = True) -> dict"
    )
    assert "dataframe" == next(iter(inspect.signature(check_dq).parameters))
    assert "dataframe" == next(iter(inspect.signature(check_sensitive_data).parameters))
    for check in (check_dq, check_sensitive_data):
        parameters = inspect.signature(check).parameters
        assert parameters["enabled"].default is True
        assert parameters["raise_on_failure"].default is False
        assert parameters["verbose"].default is True


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ({"status": "passed", "can_continue": True}, "PASS"),
        ({"status": "warning", "can_continue": True}, "WARN"),
        ({"status": "failed", "can_continue": False}, "BLOCK"),
        ({"status": "skipped", "can_continue": True}, "SKIPPED"),
    ],
)
def test_guardrail_formatter_preserves_public_statuses(capsys, result, expected) -> None:
    """The shared formatter reports the actual normalized result only."""
    print_guardrail_result("Schema", result, verbose=True, table_id="source.demo.orders")
    assert capsys.readouterr().out == (f"FabricOps Check → Schema\n  Table  source.demo.orders\n  Result {expected}\n")


def test_guardrail_formatter_verbose_false_suppresses_output(capsys) -> None:
    """Quiet checks do not emit partial headings or status lines."""
    print_guardrail_result(
        "Source Drift",
        {"status": "failed", "can_continue": False},
        verbose=False,
        source_table_id="source.demo.orders",
        target_table_id="unified.demo.curated_orders",
    )
    assert capsys.readouterr().out == ""


def test_disabled_freshness_prints_skipped(capsys) -> None:
    """Disabled public checks return and report SKIPPED without runtime setup."""
    result = check_freshness("source.demo.orders", enabled=False)
    assert result["status"] == "skipped"
    assert "Result SKIPPED" in capsys.readouterr().out
