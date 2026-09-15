"""Tests for standardized public Guardrail status output."""

from __future__ import annotations

import inspect

import pytest

from fabricops_kit import (
    check_dq,
    check_freshness,
    check_schema,
    check_sensitive_data,
    check_source_drift,
)
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


@pytest.mark.parametrize(
    "call",
    [
        lambda: check_schema(table_id="source.demo.orders", enabled=False),
        lambda: check_dq(object(), table_id="source.demo.orders", enabled=False),
        lambda: check_freshness("source.demo.orders", enabled=False),
        lambda: check_source_drift(
            "source.demo.orders",
            target_table_id="unified.demo.curated_orders",
            enabled=False,
        ),
        lambda: check_sensitive_data(object(), table_id="unified.demo.curated_orders", enabled=False),
    ],
)
def test_disabled_runtime_checks_explain_that_no_evaluation_ran(capsys, call) -> None:
    """Disabled checks remain explicit about what FabricOps skipped."""
    result = call()
    output = capsys.readouterr().out
    assert result["status"] == "skipped"
    assert "Result SKIPPED" in output
    assert "Details disabled explicitly" in output


def test_disabled_check_verbose_false_stays_quiet(capsys) -> None:
    """Detail output follows the same verbose switch as the normalized status."""
    check_freshness("source.demo.orders", enabled=False, verbose=False)
    assert capsys.readouterr().out == ""
