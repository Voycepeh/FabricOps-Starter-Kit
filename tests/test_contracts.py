import pytest

pytestmark = pytest.mark.contract
from fabricops_kit.handover import build_handover, build_handover_record, render_handover_markdown


def _runtime_context():
    return {
        "run_id": "run-1",
        "dataset_name": "orders",
        "environment": "dev",
        "source_table": "raw.orders",
        "target_table": "curated.orders",
        "started_at_utc": "2026-01-01T00:00:00Z",
    }


def test_handover_generation_smoke_for_failed_and_warning_paths():
    failed = build_handover(runtime_context=_runtime_context(), quality_result={"status": "failed", "can_continue": False})
    assert failed["overall_status"] == "failed"
    assert failed["can_continue"] is False

    warning = build_handover(runtime_context=_runtime_context(), quality_result={"status": "warning", "can_continue": True})
    assert warning["overall_status"] == "warning"


def test_handover_markdown_and_record_are_renderable():
    summary = build_handover(runtime_context=_runtime_context(), quality_result={"status": "passed", "can_continue": True})
    markdown = render_handover_markdown(summary)
    record = build_handover_record(summary)

    assert "Handover Summary" in markdown
    assert record["run_id"] == "run-1"
    assert "summary_markdown" in record
