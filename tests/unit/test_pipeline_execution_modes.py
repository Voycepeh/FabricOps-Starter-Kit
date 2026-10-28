"""Focused execution-mode policy coverage."""

from datetime import UTC, datetime
from types import MappingProxyType

import pytest

from fabricops_kit import setup_pipeline
from fabricops_kit.pipeline import shared


def _plan(mode: str) -> shared.PipelineExecutionPlan:
    plan = shared.PipelineExecutionPlan(
        mode,
        "dev",
        "notebook",
        f"run-{mode}",
        "{}",
        "{}",
        "{}",
        MappingProxyType({
            "config": {},
            "scope_workspace_id": "dev",
            "_pipeline_bindings": {},
        }),
        pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52",
    )
    plan.evidence["boundary_completed"] = True
    return plan


@pytest.mark.parametrize(
    ("mode", "persistent"),
    [("dry_run", False), ("ungoverned", True), ("governed", True)],
)
def test_three_execution_modes_have_explicit_persistence_policy(mode, persistent):
    """Only modes that perform real writes may persist operational state."""
    assert _plan(mode).permits_persistence is persistent


def test_public_setup_accepts_only_three_display_names():
    """Reject obsolete and internal mode spellings at the public boundary."""
    for obsolete in ("Test", "Live", "testing", "live", ""):
        with pytest.raises(ValueError, match="Dry Run, Ungoverned or Governed"):
            setup_pipeline(pipeline_mode=obsolete)


def test_dry_run_finalization_is_session_only(monkeypatch):
    """Dry Run finalization must not merge a pipeline-run row."""
    plan = _plan("dry_run")
    persisted = []
    monkeypatch.setattr(shared, "_merge_pipeline_run_row", lambda *args, **kwargs: persisted.append(args))

    result = shared.finalize_pipeline_run(plan)

    assert result["execution_mode"] == "dry_run"
    assert result["status"] == "incomplete"
    assert not persisted


def test_persisted_mode_values_require_no_metadata_schema_change():
    """Read new and historical string values through the existing schema."""
    for mode in ("testing", "live", "dry_run", "ungoverned", "governed"):
        row = {
            "run_id": mode,
            "pipeline_id": "8f32a471-6c91-4b7e-9d13-2f0c947eab52",
            "approval_id": None,
            "execution_mode": mode,
            "workspace_id": "dev",
            "started_at": datetime.now(UTC),
            "completed_at": None,
            "status": "incomplete",
            "activation_revision": None,
            "boundary_completed": False,
            "operations": [],
            "profiling": [],
            "warnings_json": "[]",
            "failures": [],
        }
        assert shared.validate_pipeline_run(row)["execution_mode"] == mode

