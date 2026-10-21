"""Governance widget exercises actual candidate controls and backend release validation."""
# ruff: noqa: D103, F811
import importlib

import pytest

from tests.unit.test_activated_pipeline import authority  # noqa: F401
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401

module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")


@pytest.fixture
def render(authority, monkeypatch):
    from IPython import display as ip
    monkeypatch.setattr(ip, "display", lambda *_: None)
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: ({}, "canary", authority.context))
    monkeypatch.setattr(module, "metadata_records", importlib.import_module("fabricops_kit.activated_pipeline.shared").metadata_records)
    monkeypatch.setattr(module, "read_activation_state", authority.read)
    return lambda **kw: module.widget_activate_pipeline(context=authority.context, executable_path=str(authority.executable), **kw)


def test_single_pipeline_review_and_one_approval(authority, render):
    _, run = authority.candidate()
    widget = render(pipeline_id="A")
    assert widget["additional_runs"].layout.display == "none"
    assert widget["activate"].disabled
    widget["candidate_controls"][run["run_id"]]["version"].value = "1"
    assert widget["review_release"]()["ready"]
    with pytest.raises(ValueError, match="explicitly approve"):
        widget["perform_activation"]()
    widget["confirmed"].value = True
    assert not widget["activate"].disabled
    assert widget["perform_activation"]()["pipelines"]["A"]["testing_run_id"] == run["run_id"]


def test_dependency_controls_show_missing_tests_and_coordinated_candidates(authority, render):
    _, a3 = authority.candidate("A"); _, b3 = authority.candidate("B", roles=("source",))
    authority.approve(a3); authority.approve(b3)
    _, a4 = authority.candidate("A", version=4); _, b4 = authority.candidate("B", version=4, roles=("source",))
    widget = render(pipeline_id="A")
    widget["run_select"].value = a4["run_id"]
    assert widget["additional_runs"].layout.display != "none"
    widget["candidate_controls"][a4["run_id"]]["version"].value = "4"
    report = widget["review_release"]()
    assert report["missing_pipelines"] == ["B"] and not report["ready"]
    widget["additional_runs"].value = (b4["run_id"],)
    widget["candidate_controls"][b4["run_id"]]["version"].value = "4"
    assert widget["review_release"]()["ready"]
    widget["confirmed"].value = True
    result = widget["perform_activation"]()
    assert set(result["pipelines"]) == {"A", "B"}


def test_review_is_invalidated_when_candidate_configuration_changes(authority, render):
    _, run = authority.candidate()
    widget = render()
    controls = widget["candidate_controls"][run["run_id"]]
    controls["version"].value = "1"
    widget["review_release"]()
    widget["confirmed"].value = True
    controls["version"].value = "2"
    assert widget["activate"].disabled and not widget["confirmed"].value
    with pytest.raises(ValueError): widget["perform_activation"]()


def test_empty_widget_does_not_mutate_authority(authority, render):
    token = authority.central["token"]
    widget = render()
    assert widget["eligible_runs"] == [] and widget["activate"].disabled
    assert authority.central["token"] == token


def test_unchanged_shared_contract_keeps_coordination_controls_hidden(authority, render):
    _, a = authority.candidate("A")
    authority.approve(a)
    _, b = authority.candidate("B", roles=("source",))
    widget = render(pipeline_id="B")
    assert widget["run_select"].value == b["run_id"]
    assert widget["additional_runs"].layout.display == "none"
    widget["candidate_controls"][b["run_id"]]["version"].value = "1"
    assert widget["review_release"]()["ready"]


def test_old_or_unbounded_evidence_is_excluded_before_rendering(authority, render):
    import json
    _, run = authority.candidate()
    summary = json.loads(run["operation_summary_json"])
    summary.pop("boundary_completed")
    run["operation_summary_json"] = json.dumps(summary)
    widget = render()
    assert widget["eligible_runs"] == [] and widget["activate"].disabled
