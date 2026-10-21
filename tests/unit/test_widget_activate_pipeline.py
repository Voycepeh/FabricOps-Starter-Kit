"""The Governance widget and headless service enforce the same complete-run gate."""
# ruff: noqa: D103, F811
import importlib
import pytest
from tests.unit.test_activated_pipeline import approved_runtime  # noqa: F401
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401

# Import before fixtures patch shared services; otherwise imported function references
# can retain a fixture closure after monkeypatch restores the shared module.
importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")


def test_widget_review_confirmation_and_service_activation(approved_runtime, monkeypatch):
    state=approved_runtime
    _,run=state.candidate()
    module=importlib.import_module('fabricops_kit.widgets.widget_activate_pipeline')
    from fabricops_kit.activated_pipeline import shared
    monkeypatch.setattr(module,'metadata_records',shared.metadata_records)
    monkeypatch.setattr('IPython.display.display',lambda *a,**kw:None)
    ui=module.widget_activate_pipeline(pipeline_id='orders',executable_path=str(state.executable),context=state.context)
    assert [row['run_id'] for row in ui['eligible_runs']]==[run['run_id']]
    assert ui['activate'].disabled
    assert 'fabricops-governance' in ui['widget']._dom_classes
    with pytest.raises(ValueError): ui['perform_activation']()
    ui['pipeline_name'].value='Orders'
    ui['pipeline_version'].value='1'
    ui['reviewed'].value=True
    ui['confirmed'].value=True
    assert not ui['activate'].disabled
    assert all(text in ui['details'].value for text in ['Exact frozen contracts','Code, configuration','Guardrail evidence','Warnings','Exact Agreement',run['candidate_fingerprint']])
    row=ui['perform_activation']()
    assert row['testing_run_id']==run['run_id'] and ui['activation_result']==row
    assert ui['activate'].disabled


def test_widget_cannot_bypass_changed_evidence(approved_runtime,monkeypatch):
    state=approved_runtime
    _,run=state.candidate()
    module=importlib.import_module('fabricops_kit.widgets.widget_activate_pipeline')
    from fabricops_kit.activated_pipeline import shared
    monkeypatch.setattr(module,'metadata_records',shared.metadata_records)
    monkeypatch.setattr('IPython.display.display',lambda *a,**kw:None)
    ui=module.widget_activate_pipeline(pipeline_id='orders',executable_path=str(state.executable),context=state.context)
    ui['pipeline_version'].value='1'
    ui['reviewed'].value=True
    ui['confirmed'].value=True
    run['status']='incomplete'
    with pytest.raises(ValueError,match='complete successful'): ui['perform_activation']()
    assert not state.versions
    ui['pipeline_version'].value='2'
    assert not ui['reviewed'].value and not ui['confirmed'].value and ui['activate'].disabled


def test_widget_filters_corrupt_and_contract_free_candidates(approved_runtime,monkeypatch):
    import copy
    import json
    state=approved_runtime
    _,run=state.candidate()
    bad=copy.deepcopy(run);bad['run_id']='corrupt';bad['candidate_json']='invalid-json'
    state.saved['corrupt']=bad
    bad=copy.deepcopy(run);bad['run_id']='contract-free'
    summary=json.loads(bad['operation_summary_json']);summary['frozen_contracts'][0]['contract']=None
    bad['operation_summary_json']=json.dumps(summary);state.saved['contract-free']=bad
    module=importlib.import_module('fabricops_kit.widgets.widget_activate_pipeline')
    from fabricops_kit.activated_pipeline import shared
    monkeypatch.setattr(module,'metadata_records',shared.metadata_records)
    monkeypatch.setattr('IPython.display.display',lambda *a,**kw:None)
    ui=module.widget_activate_pipeline(pipeline_id='orders',context=state.context)
    assert [row['run_id'] for row in ui['eligible_runs']]==[run['run_id']]
