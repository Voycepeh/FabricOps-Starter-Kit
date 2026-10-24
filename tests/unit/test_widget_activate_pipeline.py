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
    monkeypatch.setattr(ip, "display", lambda *_, **__: None)
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: ({}, "canary", authority.context))
    monkeypatch.setattr(module, "metadata_records", importlib.import_module("fabricops_kit.activated_pipeline.shared").metadata_records)
    monkeypatch.setattr(module, "read_activation_state", authority.read)
    return lambda **kw: module.widget_activate_pipeline(context=authority.context, **kw)


def test_single_pipeline_review_and_one_approval(authority, render):
    _, run = authority.candidate()
    widget = render(pipeline_id="4c7ae400-85ab-4023-9427-e8fde20bd596")
    assert widget["additional_runs"].layout.display == "none"
    assert widget["activate"].disabled
    widget["candidate_controls"][run["run_id"]]["version"].value = "1"
    assert widget["review_release"]()["ready"]
    with pytest.raises(ValueError, match="explicitly approve"):
        widget["perform_activation"]()
    widget["confirmed"].value = True
    assert not widget["activate"].disabled
    assert widget["perform_activation"]()["pipelines"]["4c7ae400-85ab-4023-9427-e8fde20bd596"]["testing_run_id"] == run["run_id"]


def test_dependency_controls_show_missing_tests_and_coordinated_candidates(authority, render):
    _, a3 = authority.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596"); _, b3 = authority.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", roles=("source",))
    authority.approve(a3); authority.approve(b3)
    _, a4 = authority.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", version=4); _, b4 = authority.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", version=4, roles=("source",))
    widget = render(pipeline_id="4c7ae400-85ab-4023-9427-e8fde20bd596")
    widget["run_select"].value = a4["run_id"]
    assert widget["additional_runs"].layout.display != "none"
    widget["candidate_controls"][a4["run_id"]]["version"].value = "4"
    report = widget["review_release"]()
    assert report["missing_pipelines"] == ["f5ee4669-5b76-4baf-9875-6cfecba2e031"] and not report["ready"]
    widget["additional_runs"].value = (b4["run_id"],)
    widget["candidate_controls"][b4["run_id"]]["version"].value = "4"
    assert widget["review_release"]()["ready"]
    widget["confirmed"].value = True
    result = widget["perform_activation"]()
    assert set(result["pipelines"]) == {"4c7ae400-85ab-4023-9427-e8fde20bd596", "f5ee4669-5b76-4baf-9875-6cfecba2e031"}


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
    _, a = authority.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596")
    authority.approve(a)
    _, b = authority.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", roles=("source",))
    widget = render(pipeline_id="f5ee4669-5b76-4baf-9875-6cfecba2e031")
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


@pytest.mark.parametrize('missing', [('table1',), ('table0', 'table1')])
@pytest.mark.parametrize('has_eligible_run', [False, True])
def test_missing_contract_runs_show_diagnostics_but_cannot_be_reviewed(authority, render, missing, has_eligible_run):
    """Mixed and contract-free completion stay visible without granting approval."""
    import json
    from copy import deepcopy
    from dataclasses import replace
    from fabricops_kit.pipeline import shared as pipeline

    previous, _ = authority.candidate(roles=('source', 'target'))
    contracts = json.loads(previous.contracts_json)
    for table_id in missing:
        contracts[table_id] = None
    plan = replace(previous, plan_id=previous.plan_id + '-mixed', contracts_json=json.dumps(contracts), evidence={}, results=[])
    with plan:
        authority.operation(plan, 0)
        authority.operation(plan, 1)
    run = plan.run_result
    assert run['status'] == ('succeeded' if len(missing) == 1 else 'ungoverned_completed')
    if not has_eligible_run:
        authority.saved.clear()
    authority.saved[run['run_id']] = run
    before = deepcopy(authority.central)
    widget = render(pipeline_id='4c7ae400-85ab-4023-9427-e8fde20bd596')
    notice = next(
        child for child in widget['widget'].children if 'Testing completed, but these runs cannot activate.' in str(getattr(child, 'value', '')))
    assert run['run_id'] in notice.value
    for table_id in missing:
        assert table_id in notice.value
    assert run not in widget['eligible_runs']
    assert run['run_id'] not in {value for _, value in widget['run_select'].options}
    assert run['run_id'] not in {value for _, value in widget['additional_runs'].options}
    assert widget['activate'].disabled
    if has_eligible_run:
        selected = widget['run_select'].value
        widget['candidate_controls'][selected]['version'].value = 'review-fix'
        assert widget['review_release']()['ready']
        assert run['run_id'] in notice.value
    else:
        review = next(child for child in widget['widget'].children if getattr(child, 'description', '') == 'Review complete release')
        assert review.disabled
        with pytest.raises(ValueError, match='No eligible Testing run selected'):
            widget['review_release']()
        with pytest.raises(ValueError, match='explicitly approve'):
            widget['perform_activation']()
    assert authority.central == before


def test_missing_coverage_notice_escapes_identifiers_and_handles_malformed_rows(authority, render):
    """Run metadata is diagnostic text and never trusted HTML or approval authority."""
    import json
    _, run = authority.candidate()
    candidate = json.loads(run['candidate_json'])
    summary = json.loads(run['operation_summary_json'])
    table_id = '<script>example</script>'
    candidate['participants'][0].update(table_id=table_id, contract=None)
    summary['frozen_contracts'][0].update(table_id=table_id, contract=None)
    run.update(candidate_json=json.dumps(candidate), operation_summary_json=json.dumps(summary))
    widget = render(pipeline_id='4c7ae400-85ab-4023-9427-e8fde20bd596')
    notice = next(child for child in widget['widget'].children if 'Testing completed, but these runs cannot activate.' in str(getattr(child, 'value', '')))
    assert '&lt;script&gt;example&lt;/script&gt;' in notice.value
    assert table_id not in notice.value
    assert widget['eligible_runs'] == [] and widget['activate'].disabled
    candidate['participants'] = ['invalid']
    summary['frozen_contracts'] = [None]
    run.update(candidate_json=json.dumps(candidate), operation_summary_json=json.dumps(summary))
    assert module._missing_contracts(run) == []


def test_detached_widget_evidence_cannot_replace_committed_run(authority, render):
    _, run = authority.candidate()
    widget = render()
    widget['candidate_controls'][run['run_id']]['version'].value = '1'
    assert widget['review_release']()['ready']
    widget['confirmed'].value = True
    widget['eligible_runs'][0]['status'] = 'failed'
    assert widget['perform_activation']()['pipelines']
    assert authority.saved[run['run_id']]['status'] == 'succeeded'


def test_committed_failure_after_review_prevents_activation(authority, render):
    _, run = authority.candidate()
    widget = render()
    widget['candidate_controls'][run['run_id']]['version'].value = '1'
    assert widget['review_release']()['ready']
    widget['confirmed'].value = True
    authority.saved[run['run_id']]['status'] = 'failed'
    with pytest.raises(ValueError, match='complete successful'):
        widget['perform_activation']()
    assert not authority.current()['pipelines']
