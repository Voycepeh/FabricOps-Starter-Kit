"""Tests for generated artifact ownership validation selection."""

from __future__ import annotations

import subprocess

import scripts.validate_generated_artifact_ownership as validation


def _selected_names(*paths: str) -> set[str]:
    return {check.name for check in validation.select_checks(paths)}


def test_source_public_callable_change_selects_call_flow_and_reference_checks() -> None:
    """Source package changes require call-flow and reference freshness checks."""
    names = _selected_names("src/fabricops_kit/io/read_lakehouse_table.py")

    assert names == {"public call-flow architecture contract", "individual function reference pages"}


def test_source_public_callable_change_skips_dashboard_html() -> None:
    """Source package changes do not require dashboard HTML freshness."""
    names = _selected_names("src/fabricops_kit/io/read_lakehouse_table.py")

    assert "public call-flow dashboard HTML" not in names


def test_reference_generator_change_requires_reference_generation() -> None:
    """Reference generator changes require individual reference page freshness."""
    names = _selected_names("scripts/generate_individual_function_reference_pages.py")

    assert names == {"individual function reference pages", "metadata reference pages"}


def test_metadata_schema_change_requires_metadata_reference_generation() -> None:
    """Metadata schema changes include the scoped metadata check alongside source-owned checks."""
    names = _selected_names("src/fabricops_kit/config/metadata_schemas.py")

    assert names == {
        "public call-flow architecture contract",
        "individual function reference pages",
        "metadata reference pages",
    }


def test_reference_check_includes_all_generator_owned_surfaces() -> None:
    """Reference freshness checks include every generator-owned output surface."""
    assert validation.REFERENCE_CHECK.diff_paths == (
        "docs/api/reference",
        "docs/reference/index.md",
        "docs/reference/function-call-graph.md",
    )


def test_metadata_reference_check_is_scoped_to_metadata_surfaces() -> None:
    """Metadata freshness checks should stay scoped to metadata docs only."""
    assert validation.METADATA_REFERENCE_CHECK.diff_paths == (
        "docs/reference/metadata.md",
        "docs/reference/metadata",
    )


def test_dashboard_generator_or_frontend_change_requires_dashboard_generation() -> None:
    """Dashboard generator and frontend changes require dashboard HTML freshness."""
    generator_names = _selected_names("scripts/generate_public_function_call_flows_dashboard.py")
    frontend_names = _selected_names("frontend/src/dashboard.ts")

    assert generator_names == {"public call-flow dashboard HTML"}
    assert frontend_names == {"public call-flow dashboard HTML"}


def test_mixed_change_triggers_all_directly_affected_checks() -> None:
    """Mixed ownership changes require all directly affected generated artifact checks."""
    names = _selected_names(
        "src/fabricops_kit/__init__.py",
        "scripts/generate_individual_function_reference_pages.py",
        "scripts/generate_public_function_call_flows_dashboard.py",
    )

    assert names == {
        "public call-flow architecture contract",
        "individual function reference pages",
        "metadata reference pages",
        "public call-flow dashboard HTML",
    }


def test_stale_public_call_flow_json_fails_validation(monkeypatch) -> None:
    """A stale public call-flow JSON diff still fails ownership validation."""
    completed = subprocess.CompletedProcess(args=["git"], returncode=1)

    def fake_run(command, **kwargs):  # noqa: ANN001, ANN202
        if command[:3] == ["git", "diff", "--exit-code"]:
            return completed
        return subprocess.CompletedProcess(args=command, returncode=0)

    monkeypatch.setattr(validation.subprocess, "run", fake_run)
    monkeypatch.setattr(validation, "restore_generated_metadata_and_page_timestamps", lambda **kwargs: None)

    assert validation.validate(["src/fabricops_kit/__init__.py"]) == 1
